"""Contract tests for the opt-in GitOps National Parks full stack.

The original one-ConfigMap Module 2 lab remains unchanged and isolated.
"""
import json
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
GITOPS = ROOT / "content/modules/ROOT/examples/module02-gitops"
FULL = GITOPS / "fullstack"
APP = GITOPS / "fullstack-application-example.yaml"


def docs_for(name):
    return [x for x in yaml.safe_load_all((FULL / name).read_text()) if x]


class FullStackGitOpsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resources = {}
        cls.all_resources = []
        fullstack = yaml.safe_load((FULL / "kustomization.yaml").read_text())
        cls.manifest_names = fullstack["resources"]
        for name in cls.manifest_names:
            for obj in docs_for(name):
                key = (obj["kind"], obj["metadata"]["name"])
                if key in cls.resources:
                    raise AssertionError(f"duplicate manifest {key}")
                cls.resources[key] = obj
                cls.all_resources.append(obj)
        cls.app = yaml.safe_load(APP.read_text())

    def res(self, kind, name):
        return self.resources[(kind, name)]

    def test_fullstack_is_opt_in_and_no_namespace_manifest(self):
        baseline = yaml.safe_load((GITOPS / "kustomization.yaml").read_text())
        self.assertEqual(baseline["resources"], ["national-parks-gitops-info.yaml"])
        self.assertEqual(len(self.manifest_names), 7)
        self.assertEqual(len(self.all_resources), 21)
        self.assertFalse(any(obj["kind"] == "Namespace" for obj in self.all_resources))
        self.assertFalse(any("namespace" in obj["metadata"] for obj in self.all_resources))
        self.assertEqual(
            self.app["spec"]["source"]["path"],
            "content/modules/ROOT/examples/module02-gitops/fullstack",
        )
        self.assertEqual(self.app["metadata"]["namespace"], "user-xtm9x-demo")
        self.assertEqual(self.app["spec"]["destination"]["namespace"],
                         "user-xtm9x-gitops")
        self.assertEqual(self.app["spec"]["source"]["targetRevision"], "main")

    def test_auto_sync_is_safe_with_openshift_build_trigger(self):
        sync = self.app["spec"]["syncPolicy"]
        self.assertEqual(sync["automated"], {
            "enabled": True, "prune": False, "selfHeal": True,
        })
        self.assertIn("RespectIgnoreDifferences=true", sync["syncOptions"])
        self.assertEqual(self.app["spec"]["ignoreDifferences"], [{
            "group": "apps",
            "kind": "Deployment",
            "name": "nationalparks",
            "jsonPointers": ["/spec/template/spec/containers/0/image"],
        }])
        deployment = self.res("Deployment", "nationalparks")
        triggers = json.loads(deployment["metadata"]["annotations"]
                              ["image.openshift.io/triggers"])
        self.assertEqual(len(triggers), 1)
        self.assertEqual(triggers[0]["from"],
                         {"kind": "ImageStreamTag", "name": "nationalparks:latest"})
        self.assertEqual(triggers[0]["fieldPath"],
                         'spec.template.spec.containers[?(@.name=="nationalparks")].image')
        self.assertFalse(triggers[0]["paused"])
        self.assertEqual(deployment["spec"]["template"]["spec"]["containers"][0]["name"],
                         "nationalparks")

    def test_all_three_workloads_with_matched_services(self):
        for name in ("mongodb-nationalparks", "nationalparks", "parksmap"):
            deployment = self.res("Deployment", name)
            service = self.res("Service", name)
            labels = deployment["spec"]["template"]["metadata"]["labels"]
            for key, value in service["spec"]["selector"].items():
                self.assertEqual(labels[key], value)
            self.assertEqual(deployment["spec"]["replicas"], 1)
        for name, svc in (("parksmap", "parksmap"),
                          ("national-parks-app", "nationalparks")):
            route = self.res("Route", name)
            self.assertEqual(route["spec"]["to"]["name"], svc)
            self.assertEqual(route["spec"]["tls"]["termination"], "edge")
            self.assertEqual(route["spec"]["tls"]["insecureEdgeTerminationPolicy"],
                             "Redirect")
            self.assertNotIn("host", route["spec"])
        for kind in ("Route", "Service"):
            self.assertEqual(
                self.res(kind, "national-parks-app" if kind == "Route" else "nationalparks")
                    ["metadata"]["labels"]["type"], "parksmap-backend",
            )

    def test_database_is_modern_persistent_and_correctly_wired(self):
        mongodb = self.res("Deployment", "mongodb-nationalparks")
        mongo = mongodb["spec"]["template"]["spec"]["containers"][0]
        self.assertEqual(mongo["image"],
                         "quay.io/mongodb/mongodb-community-server:8.0.32-ubi9-slim")
        self.assertEqual(mongo["envFrom"],
                         [{"secretRef": {"name": "nationalparks-mongodb-parameters"}}])
        self.assertEqual(self.res("Service", "mongodb-nationalparks")["spec"]["ports"][0]
                         ["port"], 27017)
        self.assertEqual(self.res("Service", "mongodb-nationalparks")["spec"]["ports"][0]
                         ["targetPort"], "mongodb")
        claim = self.res("PersistentVolumeClaim", "mongodb-nationalparks-data")
        self.assertEqual(claim["spec"]["resources"]["requests"]["storage"], "1Gi")
        self.assertEqual(self.res("ConfigMap", "mongodb-nationalparks-bootstrap")
                         ["data"]["create-app-user.js"].count("createUser("), 1)
        self.assertEqual(mongodb["spec"]["template"]["spec"]["volumes"][0]
                         ["persistentVolumeClaim"]["claimName"],
                         "mongodb-nationalparks-data")
        backend = self.res("Deployment", "nationalparks")
        self.assertEqual(backend["spec"]["template"]["spec"]["containers"][0]
                         ["envFrom"][0]["secretRef"]["name"],
                         "nationalparks-mongodb-parameters")

    def test_backend_build_matches_module_one(self):
        build = self.res("BuildConfig", "nationalparks")
        self.assertEqual(build["spec"]["source"]["git"]["uri"],
                         "https://github.com/openshift-roadshow/nationalparks-py.git")
        self.assertEqual(build["spec"]["source"]["git"]["ref"], "master")
        self.assertEqual(build["spec"]["strategy"]["type"], "Docker")
        self.assertEqual(build["spec"]["output"]["to"]["name"], "nationalparks:latest")
        self.assertEqual(build["spec"]["triggers"], [{"type": "ConfigChange"}])
        self.assertEqual(self.res("ImageStream", "nationalparks")["spec"]["lookupPolicy"],
                         {"local": True})

    def test_credentials_not_stored_in_public_git(self):
        self.assertFalse(any(x["kind"] == "Secret" for x in self.all_resources))
        sa = self.res("ServiceAccount", "nationalparks-credentials-bootstrap")
        role = self.res("Role", sa["metadata"]["name"])
        binding = self.res("RoleBinding", sa["metadata"]["name"])
        self.assertEqual(role["rules"][0]["resources"], ["secrets"])
        self.assertEqual(role["rules"][0]["verbs"], ["create"])
        self.assertEqual(role["rules"][1]["verbs"], ["get"])
        self.assertEqual(role["rules"][1]["resourceNames"],
                         ["nationalparks-mongodb-parameters"])
        self.assertEqual(binding["roleRef"]["name"], sa["metadata"]["name"])
        self.assertEqual(self.res("Job", sa["metadata"]["name"])["spec"]["template"]
                         ["spec"]["serviceAccountName"], sa["metadata"]["name"])
        cmd = self.res("Job", sa["metadata"]["name"])["spec"]["template"]["spec"]\
                  ["containers"][0]["args"][0]
        self.assertIn("/dev/urandom", cmd)
        self.assertIn("oc create secret generic", cmd)
        self.assertIn("oc get secret nationalparks-mongodb-parameters", cmd)
        self.assertNotIn("MONGODB_PASSWORD=mongodb", (FULL / "00-mongodb-credentials.yaml").read_text())

    def test_parksmap_uses_dedicated_discovery_sa(self):
        frontend = self.res("Deployment", "parksmap")["spec"]["template"]["spec"]
        self.assertEqual(frontend["serviceAccountName"], "parksmap-discovery")
        self.assertEqual(frontend["containers"][0]["image"],
                         "quay.io/openshiftroadshow/parksmap:latest")
        role = self.res("Role", "parksmap-discovery")
        self.assertEqual({res for rule in role["rules"] for res in rule["resources"]},
                         {"routes", "services", "endpoints"})
        for rule in role["rules"]:
            self.assertNotIn("secrets", rule["resources"])
            self.assertFalse({"create", "update", "patch", "delete"} &
                             set(rule["verbs"]))

    def test_seed_job_checks_empty_collection_before_mutating_load(self):
        job = self.res("Job", "nationalparks-seed-data")
        self.assertEqual(job["metadata"]["annotations"]["argocd.argoproj.io/hook"],
                         "PostSync")
        cmd = job["spec"]["template"]["spec"]["containers"][0]["args"][0]
        self.assertIn("/ws/data/all", cmd)
        self.assertIn('if [ "$data" = "[]" ]; then', cmd)
        self.assertIn("/ws/data/load", cmd)
        self.assertLess(cmd.index("/ws/data/all"), cmd.index("/ws/data/load"))


if __name__ == "__main__":
    unittest.main()
