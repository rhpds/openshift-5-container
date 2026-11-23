"""Regressions for the student browser checks and the independent tenant probe."""
import importlib.util
import io
import re
import unittest
from contextlib import redirect_stdout
from copy import deepcopy
from pathlib import Path
from unittest.mock import Mock, patch

import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


release = load_module("release", "content/modules/ROOT/attachments/check-release.py")
probe = load_module("probe", "automation/gitops/bootstrap-infra/files/probe.py")
NS = "user-test-gitops"
REV = "deployment.kubernetes.io/revision"


def owner(uid):
    return [{"uid": uid, "controller": True}]


class ReleaseChecks(unittest.TestCase):
    def setUp(self):
        self.container = {"name": "weathernow", "image": release.WEATHER + "latest",
                          "ports": [{"name": "http", "containerPort": 8080}],
                          "readinessProbe": {"tcpSocket": {"port": "http"}}}
        self.template = {"containers": [self.container]}
        self.dep = {"metadata": {"uid": "deploy", "generation": 4, "annotations": {REV: "3"}},
                    "spec": {"replicas": 1, "template": {"spec": self.template}},
                    "status": {"observedGeneration": 4, "replicas": 1, "updatedReplicas": 1,
                               "readyReplicas": 1, "availableReplicas": 1}}
        self.state = {"name": "weathernow", "ready": True}
        self.pod = {"metadata": {"name": "current-pod", "uid": "new-pod", "ownerReferences": owner("new-rs")},
                    "spec": self.template, "status": {"phase": "Running", "containerStatuses": [self.state]}}
        self.old = deepcopy(self.pod)
        self.old["metadata"].update(uid="old-pod", name="old-pod", ownerReferences=owner("old-rs"))
        def rs(uid, revision):
            return {"metadata": {"uid": uid, "ownerReferences": owner("deploy"), "annotations": {REV: revision}}}
        self.events = []
        self.resources = {"deployment/weathernow": self.dep, "replicasets": {"items": [rs("old-rs", "2"), rs("new-rs", "3")]},
                          "pods": {"items": [self.old, self.pod]}, "events": {"items": self.events},
                          "route/weathernow": {"spec": {"host": "weathernow.example"}}}
        self.get = self.enter_patch(patch.object(release, "get", side_effect=lambda ns, kind, *args: self.resources[kind]))
        self.route = self.enter_patch(patch.object(release, "run", return_value="200"))

    def enter_patch(self, patcher):
        value = patcher.start()
        self.addCleanup(patcher.stop)
        return value

    def check(self, mode):
        return release.weather_evidence(NS, mode, "Healthy")

    def test_old_ready_pod_cannot_pass_when_its_replacement_is_unready(self):
        self.state["ready"] = False
        self.assertIsNone(self.check("healthy"))
        self.route.assert_not_called()

    def test_generation_template_and_each_replica_count_must_agree(self):
        self.assertIn("current-pod ready", self.check("healthy"))
        for key in ("observedGeneration", "replicas", "updatedReplicas", "readyReplicas", "availableReplicas"):
            with self.subTest(key=key), patch.dict(self.dep["status"], {key: 0}):
                self.assertIsNone(self.check("healthy"))
        with patch.dict(self.dep["spec"]["template"], {"spec": {"containers": []}}):
            self.assertIsNone(self.check("healthy"))

    def test_route_failure_or_terminating_current_pod_cannot_pass(self):
        self.route.return_value = "503"
        self.assertIsNone(self.check("healthy"))
        self.route.return_value = "200"
        self.pod["metadata"]["deletionTimestamp"] = "2026-01-01T00:00:00Z"
        self.assertIsNone(self.check("healthy"))

    def test_readiness_fault_needs_warning_for_this_pod_and_this_probe(self):
        self.container["readinessProbe"]["tcpSocket"]["port"] = 18080
        self.state["ready"] = False
        event = {"type": "Warning", "reason": "Unhealthy", "message": "Readiness probe failed on 18080",
                 "involvedObject": {"uid": "old-pod"}}
        self.events.append(event)
        self.assertIsNone(self.check("readiness-fault"))
        event["involvedObject"]["uid"] = "new-pod"
        with patch.dict(event, {"message": "Liveness probe failed on 8080"}):
            self.assertIsNone(self.check("readiness-fault"))
        message = self.check("readiness-fault")
        self.assertIn("oc logs -n user-test-gitops pod/current-pod", message)
        self.get.assert_any_call(NS, "events", "--field-selector", "involvedObject.uid=new-pod")

    def test_image_fault_needs_both_the_expected_tag_and_pull_failure(self):
        bad_image = release.WEATHER + "module05-intentional-bad-tag"
        self.container["image"] = bad_image
        self.state.update(ready=False, state={"waiting": {"reason": "ImagePullBackOff"}})
        self.assertIsNone(self.check("image-fault"))
        event = {"type": "Warning", "reason": "Failed", "message": "Failed to pull image " + bad_image,
                 "involvedObject": {"uid": "old-pod"}}
        self.events.append(event)
        self.assertIsNone(self.check("image-fault"))
        event["involvedObject"]["uid"] = "new-pod"
        message = self.check("image-fault")
        self.assertIn("current-pod Failed", message)
        self.assertIn("Pod UID: new-pod", message)
        self.assertIn(bad_image, message)
        self.state["state"] = {"waiting": {"reason": "ContainerCreating"}}
        self.assertIsNone(self.check("image-fault"))

    def test_waits_for_the_requested_commit_even_when_old_argo_revision_is_healthy(self):
        host = "gitea-user-test-demo.apps.example"
        src = {"repoURL": "https://" + host + "/user-test/openshift-5-container-workspace.git",
               "targetRevision": "main", "path": "weathernow"}
        app = {"spec": {"source": src, "destination": {"server": "https://kubernetes.default.svc", "namespace": NS}}}
        def status(sha):
            return {"status": {"sync": {"status": "Synced", "revision": sha}, "health": {"status": "Healthy"}}}
        wanted = "b" * 40
        self.get.side_effect = [app, {"items": [{"spec": {"host": host}}]}, status("a" * 40), status(wanted)]
        self.route.side_effect = ["user-test", wanted + "\trefs/heads/main"]
        with patch.object(release.sys, "argv", ["check-release.py", "user-test", "weathernow-lab", "healthy"]), \
             patch.object(release.time, "monotonic", side_effect=[0, 1, 310]), \
             patch.object(release.time, "sleep") as wait, patch.object(release, "weather_evidence", return_value="ready") as evidence, \
             redirect_stdout(io.StringIO()) as output:
            release.main()
        wait.assert_called_once()
        evidence.assert_called_once_with(NS, "healthy", "Healthy")
        self.assertIn("PASS " + wanted, output.getvalue())

    def test_service_account_cannot_be_mistaken_for_the_student(self):
        self.route.return_value = "system:serviceaccount:user-test-showroom:showroom"
        with patch.object(release.sys, "argv", ["check-release.py", "user-test", "weathernow-lab", "healthy"]), \
             self.assertRaisesRegex(RuntimeError, "Sign in"):
            release.main()
        self.get.assert_not_called()


class ReferenceChecks(unittest.TestCase):
    def setUp(self):
        self.address = "10.96.0.12"
        self.spec = {"type": "ClusterIP", "clusterIP": self.address, "selector": {"app": "workshop-netcheck"},
                     "ports": [{"port": 8080, "protocol": "TCP"}]}
        self.conn = Mock()
        self.conn.getresponse.return_value.status = 200

    def observe(self, response=None):
        if response is None:
            response = (200, {"spec": self.spec})
        with patch.object(probe, "api_get", return_value=response), \
             patch.object(probe.http.client, "HTTPConnection", return_value=self.conn):
            return probe.canary_status(NS)

    def test_only_a_timeout_during_tcp_connect_is_an_isolation_observation(self):
        self.assertEqual(self.observe(), (self.address, "200"))
        self.conn.connect.side_effect = TimeoutError
        self.assertEqual(self.observe(), (self.address, "connect_timeout"))
        self.conn.connect.side_effect = ConnectionRefusedError
        self.assertEqual(self.observe(), (self.address, "ConnectionRefusedError"))
        self.conn.connect.side_effect = None
        self.conn.getresponse.side_effect = TimeoutError
        self.assertEqual(self.observe(), (self.address, "TimeoutError"))

    def test_api_errors_and_wrong_service_targets_are_inconclusive(self):
        self.assertEqual(self.observe((403, None)), (None, "service_lookup_403"))
        for change in ({"type": "ExternalName"}, {"clusterIP": "None"}, {"selector": {}}, {"ports": [{"port": 80}]}):
            with self.subTest(change=change), patch.dict(self.spec, change):
                self.assertEqual(self.observe(), (None, "unexpected_service"))
        self.conn.connect.assert_not_called()


class CanaryPolicyChecks(unittest.TestCase):
    def test_baseline_selects_only_named_clients_and_is_removed_for_isolation(self):
        guide = next((ROOT / "content/modules/ROOT/pages").glob("module-02-*.adoc")).read_text()
        manifest = re.search(r"allow_canary_clients\(\).*?<<YAML\n(.*?)\nYAML", guide, re.S).group(1)
        manifest = manifest.replace("$peer", "user-partner-gitops").replace("$LAB_NAMESPACE", "user-test-demo")
        rule = yaml.safe_load(manifest.replace("$PEER_SA", "probe-user-test"))["spec"]
        self.assertEqual(rule["podSelector"], {"matchLabels": {"app": "workshop-netcheck"}})
        self.assertEqual(rule["ingress"][0]["ports"], [{"port": 8080, "protocol": "TCP"}])
        clients = rule["ingress"][0]["from"]
        self.assertIn({"podSelector": {}}, clients)
        by_ns = {c["namespaceSelector"]["matchLabels"]["kubernetes.io/metadata.name"]: c
                 for c in clients if "namespaceSelector" in c}
        self.assertEqual(set(by_ns), {"user-test-demo", "user-partner-gitops", "lb1858-reference-tenant"})
        self.assertEqual(by_ns["lb1858-reference-tenant"]["podSelector"],
                         {"matchLabels": {"app.kubernetes.io/instance": "probe-user-test"}})
        restricted = guide.index("peer_check 200 connect_timeout")
        self.assertLess(guide.index("oc delete networkpolicy workshop-netcheck-baseline"), restricted)
        self.assertIn("allow_canary_clients &&", guide[restricted:guide.index("oc delete service workshop-netcheck")])
