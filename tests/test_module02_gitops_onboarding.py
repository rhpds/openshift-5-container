"""Contracts for the primary 45-minute Module 2 full-stack Auto-Sync lab."""

import re
import subprocess
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "content/modules/ROOT/pages/module-02-gitops-onboarding-multitenancy.adoc"
SOURCE = ROOT / "content/modules/ROOT/examples/module02-gitops"
BOOTSTRAP = ROOT / "automation/gitops/bootstrap-tenant/values.yaml"
UI_CONFIG = ROOT / "ui-config.yml"
INSTRUCTOR = ROOT / "docs/instructor/module-02-gitops-preflight.md"
SCREENSHOTS = ROOT / "content/modules/ROOT/images/MODULE02-SCREENSHOTS.md"


class GitOpsWorkshopTests(unittest.TestCase):
    def test_five_missions_and_three_interactive_predictions(self):
        guide = GUIDE.read_text()
        missions = re.findall(r"^== Mission [1-5]:", guide, re.MULTILINE)
        self.assertEqual(len(missions), 5)
        self.assertEqual(guide.count("[%collapsible]"), 3)
        self.assertIn("approximately 45 minutes", guide)
        self.assertIn("full National Parks stack", guide)
        self.assertIn("automatically", guide)
        self.assertIn("Module 1", guide)
        self.assertNotIn("== Optional advanced extension", guide)
        self.assertNotIn("manages **one harmless ConfigMap**", guide)
        self.assertIn("a healthy, synced configmap-only application", guide.lower())
        self.assertIn("Healthy/Synced ConfigMap-only tree", guide)

    def test_twelve_labelled_screenshot_placeholders_and_checklist(self):
        guide = GUIDE.read_text()
        checklist = SCREENSHOTS.read_text()
        refs = re.findall(r"image::(module02-s\d{2}[-\w]*\.(?:svg|png))\[", guide)
        self.assertEqual(len(refs), 12, refs)
        self.assertEqual(len(set(refs)), 12)
        for name in refs:
            self.assertTrue((ROOT / "content/modules/ROOT/images" / name).is_file(),
                            name)
            self.assertIn(name.replace(".svg", ".png"), checklist)
            if name.endswith(".svg"):
                self.assertIn(
                    "SCREENSHOT NEEDED",
                    (ROOT / "content/modules/ROOT/images" / name).read_text(),
                )
        self.assertEqual(len(re.findall(r"^\| S\d{2} \|", checklist,
                                        re.MULTILINE)), 12)
        self.assertIn("Students are never instructed to upload", checklist)
        self.assertIn("Auto-Sync", checklist)
        self.assertNotIn("S07 is optional", checklist)

    def test_kustomization_default_is_full_stack(self):
        root = yaml.safe_load((SOURCE / "kustomization.yaml").read_text())
        full = yaml.safe_load((SOURCE / "fullstack/kustomization.yaml").read_text())
        self.assertEqual(root["kind"], "Kustomization")
        self.assertEqual(root["resources"], ["fullstack"])
        self.assertEqual(len(full["resources"]), 7)
        self.assertEqual(full["resources"], [
            "national-parks-gitops-info.yaml",
            "00-mongodb-credentials.yaml",
            "01-mongodb.yaml",
            "02-nationalparks-backend.yaml",
            "03-parksmap-discovery.yaml",
            "04-parksmap-frontend.yaml",
            "05-park-data-bootstrap.yaml",
        ])
        for name in full["resources"]:
            self.assertTrue((SOURCE / "fullstack" / name).is_file(), name)
        self.assertIn(
            "full-stack automated synchronization",
            (SOURCE / "fullstack/national-parks-gitops-info.yaml").read_text(),
        )

    def test_mongodb_pvc_wait_for_first_consumer_does_not_block_sync(self):
        """The PVC and its consumer must share a wave on gp3-csi clusters."""
        objects = list(yaml.safe_load_all(
            (SOURCE / "fullstack/01-mongodb.yaml").read_text()
        ))
        pvc = next(obj for obj in objects if obj.get("kind") == "PersistentVolumeClaim")
        deployment = next(
            obj for obj in objects
            if obj.get("kind") == "Deployment"
            and obj.get("metadata", {}).get("name") == "mongodb-nationalparks"
        )
        annotations = pvc["metadata"]["annotations"]
        self.assertEqual(
            annotations.get("argocd.argoproj.io/sync-wave"),
            deployment["metadata"]["annotations"].get("argocd.argoproj.io/sync-wave"),
            "A Pending WaitForFirstConsumer PVC in an earlier wave blocks its Pod",
        )
        self.assertNotIn(
            "SkipHealthCheck=true",
            annotations.get("argocd.argoproj.io/sync-options", ""),
            "Do not hide PVC provisioning failures from GitOps health",
        )
        self.assertEqual(
            deployment["spec"]["template"]["spec"]["volumes"][0]
                      ["persistentVolumeClaim"]["claimName"],
            pvc["metadata"]["name"],
        )

    def test_parksmap_discovers_ready_service_not_unmatched_route(self):
        """Legacy RouteWatcher dereferences Endpoints with its Route's name."""
        backend = list(yaml.safe_load_all(
            (SOURCE / "fullstack/02-nationalparks-backend.yaml").read_text()
        ))
        frontend = list(yaml.safe_load_all(
            (SOURCE / "fullstack/04-parksmap-frontend.yaml").read_text()
        ))
        service = next(obj for obj in backend if obj.get("kind") == "Service")
        route = next(obj for obj in backend if obj.get("kind") == "Route")
        backend_deployment = next(
            obj for obj in backend if obj.get("kind") == "Deployment"
        )
        parksmap_deployment = next(
            obj for obj in frontend if obj.get("kind") == "Deployment"
        )

        # The Service creates Endpoints/nationalparks and is the only
        # discovery target. Route/national-parks-app has no matching
        # Endpoints object and must NOT be watched by the old client.
        self.assertEqual(service["metadata"]["name"], "nationalparks")
        self.assertEqual(route["metadata"]["name"], "national-parks-app")
        self.assertEqual(service["metadata"]["labels"]["type"], "parksmap-backend")
        self.assertNotEqual(
            route["metadata"]["labels"].get("type"), "parksmap-backend"
        )
        self.assertEqual(route["spec"]["to"]["name"], service["metadata"]["name"])

        # Start ParksMap only after the backend is Healthy, so the
        # discovered Service has a nonempty Endpoints address list.
        backend_wave = int(
            backend_deployment["metadata"]["annotations"]["argocd.argoproj.io/sync-wave"]
        )
        frontend_wave = int(
            parksmap_deployment["metadata"]["annotations"]["argocd.argoproj.io/sync-wave"]
        )
        self.assertLess(backend_wave, frontend_wave)
        self.assertEqual((backend_wave, frontend_wave), (1, 2))
        self.assertEqual(
            parksmap_deployment["spec"]["template"]["spec"]["serviceAccountName"],
            "parksmap-discovery",
        )

    def test_all_fullstack_pods_and_builds_have_quota_compliant_limits(self):
        """ClusterResourceQuota rejects pods without explicit limits.cpu."""
        count = 0
        for path in sorted((SOURCE / "fullstack").glob("*.yaml")):
            for obj in yaml.safe_load_all(path.read_text()):
                if not isinstance(obj, dict):
                    continue
                kind = obj.get("kind")
                if kind in ("Deployment", "Job"):
                    pod_spec = obj["spec"]["template"]["spec"]
                    containers = pod_spec.get("containers", []) + pod_spec.get("initContainers", [])
                elif kind == "BuildConfig":
                    # The BuildConfig resources are copied onto its build Pod.
                    containers = [{"name": "build", "resources": obj["spec"]["resources"]}]
                else:
                    continue
                for container in containers:
                    with self.subTest(file=path.name, kind=kind, container=container["name"]):
                        resources = container.get("resources", {})
                        for dimension in ("cpu", "memory"):
                            self.assertIn(
                                dimension, resources.get("requests", {}),
                                f"{path.name} {kind} needs requests.{dimension}",
                            )
                            self.assertIn(
                                dimension, resources.get("limits", {}),
                                f"{path.name} {kind} needs limits.{dimension}",
                            )
                    count += 1
        self.assertEqual(count, 6, "Check both Jobs, all 3 Deployments and the BuildConfig")

    def test_small_two_namespace_resource_profile(self):
        """Keep running Pods small without mutating completed Job templates."""
        specs = {}
        parksmap = None
        for path in sorted((SOURCE / "fullstack").glob("*.yaml")):
            for obj in yaml.safe_load_all(path.read_text()):
                if not isinstance(obj, dict):
                    continue
                kind = obj.get("kind")
                if kind in ("Deployment", "Job"):
                    container = obj["spec"]["template"]["spec"]["containers"][0]
                    specs[(kind, obj["metadata"]["name"])] = container["resources"]
                    if kind == "Deployment" and obj["metadata"]["name"] == "parksmap":
                        parksmap = container
                elif kind == "BuildConfig":
                    specs[(kind, obj["metadata"]["name"])] = obj["spec"]["resources"]

        expected = {
            ("Job", "nationalparks-credentials-bootstrap"):
                ("50m", "96Mi", "200m", "256Mi"),
            ("Deployment", "mongodb-nationalparks"):
                ("75m", "192Mi", "400m", "768Mi"),
            ("BuildConfig", "nationalparks"):
                ("100m", "256Mi", "750m", "1536Mi"),
            ("Deployment", "nationalparks"):
                ("50m", "128Mi", "250m", "384Mi"),
            ("Deployment", "parksmap"):
                ("75m", "192Mi", "500m", "768Mi"),
            ("Job", "nationalparks-seed-data"):
                ("25m", "64Mi", "200m", "192Mi"),
        }
        self.assertEqual(set(specs), set(expected))
        for key, values in expected.items():
            req_cpu, req_mem, lim_cpu, lim_mem = values
            with self.subTest(workload=key):
                self.assertEqual(specs[key]["requests"], {
                    "cpu": req_cpu, "memory": req_mem,
                })
                self.assertEqual(specs[key]["limits"], {
                    "cpu": lim_cpu, "memory": lim_mem,
                })

        java_opts = next(
            env["value"] for env in parksmap["env"]
            if env["name"] == "JAVA_TOOL_OPTIONS"
        )
        self.assertIn("-Xmx256m", java_opts)
        self.assertIn("-XX:MaxMetaspaceSize=160m", java_opts)
        self.assertIn("-XX:+UseSerialGC", java_opts)

        def cpu_milli(value):
            text = str(value)
            return int(text[:-1]) if text.endswith("m") else int(text) * 1000

        def mem_mi(value):
            text = str(value)
            if text.endswith("Mi"):
                return int(text[:-2])
            if text.endswith("Gi"):
                return int(text[:-2]) * 1024
            raise AssertionError(f"Unsupported memory unit: {value}")

        steady = {
            key: resources for key, resources in specs.items()
            if key[0] == "Deployment"
        }
        self.assertEqual(
            sum(cpu_milli(r["limits"]["cpu"]) for r in steady.values()), 1150,
        )
        self.assertEqual(
            sum(mem_mi(r["limits"]["memory"]) for r in steady.values()), 1920,
        )
        self.assertEqual(
            sum(cpu_milli(r["limits"]["cpu"]) for r in specs.values()), 2300,
        )
        self.assertEqual(
            sum(mem_mi(r["limits"]["memory"]) for r in specs.values()), 3904,
        )

        # Even a pessimistic 2x of every running Pod, build and Job fits
        # the tenant quota on paper. Other -demo resources and rollout
        # surge still need validation against the live quota.
        values = yaml.safe_load(BOOTSTRAP.read_text())
        hard = values["tenantQuota"]["hard"]
        self.assertLess(
            2 * sum(cpu_milli(r["limits"]["cpu"]) for r in specs.values()),
            cpu_milli(hard["limits.cpu"]),
        )
        self.assertLess(
            2 * sum(mem_mi(r["limits"]["memory"]) for r in specs.values()),
            mem_mi(hard["limits.memory"]),
        )

    def test_gitea_import_and_student_gate(self):
        values = yaml.safe_load(BOOTSTRAP.read_text())
        repos = {r["name"]: r for r in values["gitea"]["migrateRepos"]}
        self.assertEqual(
            repos["openshift-5-container"]["url"],
            "https://github.com/rhpds/openshift-5-container",
        )
        self.assertFalse(repos["openshift-5-container"]["private"])
        guide = GUIDE.read_text()
        instructor = INSTRUCTOR.read_text()
        self.assertIn("pre-provisioned", guide)
        self.assertIn("fullstack/kustomization.yaml", guide)
        self.assertIn("repository is stale", guide)
        self.assertIn("all ten", instructor)
        self.assertIn("AUTH_FAILED", instructor)
        self.assertIn("root kustomization.yaml", instructor)
        self.assertNotIn("api/v1/repos/migrate", guide)
        self.assertIn("check-module02-fullstack-gitea.sh", instructor)
        self.assertIn("A green Argo CD badge is not this release gate", instructor)
        checker = (ROOT / "automation/scripts/check-module02-fullstack-gitea.sh").read_text()
        self.assertIn("GIT_TERMINAL_PROMPT=0", checker)
        self.assertIn("root_is_fullstack", checker)
        self.assertIn("00-mongodb-credentials.yaml", checker)
        self.assertIn("05-park-data-bootstrap.yaml", checker)
        self.assertIn("BLOCKED:", checker)
        self.assertNotIn("git push", checker)
        subprocess.run(
            ["bash", "-n", str(ROOT / "automation/scripts/check-module02-fullstack-gitea.sh")],
            check=True,
        )
        self.assertNotIn("curl -fsS --user", guide)

    def test_namespaces_bootstrap_and_student_identity(self):
        guide = GUIDE.read_text()
        instructor = INSTRUCTOR.read_text()
        ns = (
            ROOT / "automation/gitops/bootstrap-tenant/templates/module02-namespace.yaml"
        ).read_text()
        rolebinding = (
            ROOT / "automation/gitops/bootstrap-tenant/templates/module02-student-view.yaml"
        ).read_text()
        self.assertIn("kind: Namespace", ns)
        self.assertIn("name: {{ .Values.username }}-gitops", ns)
        self.assertIn("argocd.argoproj.io/managed-by:", ns)
        self.assertIn("openshift.io/requester:", ns)
        self.assertIn("kind: RoleBinding", rolebinding)
        self.assertIn("module02-student-view", rolebinding)
        self.assertIn("oc whoami", guide)
        self.assertIn("export LAB_NAMESPACE={user}-demo", guide)
        self.assertIn("export GITOPS_NAMESPACE={user}-gitops", guide)
        self.assertIn("oc auth can-i patch deployments.apps -n openshift-config",
                      guide)
        self.assertNotIn("oc create namespace", guide)
        self.assertNotIn("kind: Namespace", (
            SOURCE / "fullstack/kustomization.yaml"
        ).read_text())

    def test_native_console_fullstack_application_and_auto_sync(self):
        guide = GUIDE.read_text()
        mission3 = guide.split("== Mission 3:", 1)[1].split(
            "== Mission 4:", 1
        )[0]
        match = re.search(
            r'\[source,yaml,subs="attributes\+"\]\n----\n(.*?)\n----',
            mission3, re.DOTALL,
        )
        self.assertIsNotNone(match, "full Application YAML required in Mission 3")
        app = yaml.safe_load(match.group(1))
        self.assertEqual(app["kind"], "Application")
        self.assertEqual(app["metadata"], {
            "name": "national-parks-settings",
            "namespace": "{user}-demo",
        })
        self.assertEqual(
            app["spec"]["source"]["repoURL"],
            "https://gitea-{user}-demo.{openshift_cluster_ingress_domain}/"
            "{user}/openshift-5-container.git",
        )
        self.assertEqual(app["spec"]["source"]["targetRevision"], "main")
        self.assertEqual(app["spec"]["source"]["path"],
                         "content/modules/ROOT/examples/module02-gitops")
        self.assertEqual(app["spec"]["destination"], {
            "server": "https://kubernetes.default.svc",
            "namespace": "{user}-gitops",
        })
        self.assertEqual(app["spec"]["syncPolicy"]["automated"],
                         {"enabled": True, "prune": False, "selfHeal": True})
        self.assertIn("RespectIgnoreDifferences=true",
                      app["spec"]["syncPolicy"]["syncOptions"])
        self.assertEqual(app["spec"]["ignoreDifferences"], [{
            "group": "apps", "kind": "Deployment", "name": "nationalparks",
            "jsonPointers": ["/spec/template/spec/containers/0/image"],
        }])
        self.assertIn("GitOps -> Applications", mission3)
        self.assertIn("*Create Application*", mission3)
        self.assertIn("Do **not** click manual Sync", mission3)
        self.assertNotIn("Select *Sync*", mission3)

    def test_complete_workloads_git_commit_and_read_only_ai(self):
        guide = GUIDE.read_text()
        for name in (
            "mongodb-nationalparks", "nationalparks", "parksmap",
            "national-parks-app", "nationalparks-mongodb-parameters",
            "mongodb-nationalparks-data", "BuildConfig", "ImageStream",
            "Gitea", "Updated through GitOps Auto-Sync",
        ):
            self.assertIn(name, guide)
        self.assertIn("/ws/data/all", guide)
        self.assertIn("PostSync", guide)
        self.assertIn("image::module02-s11-argocd-resynced.svg", guide)
        self.assertIn("Do not read Secrets or change anything.", guide)
        self.assertIn("prune: false", guide)
        self.assertNotIn("oc patch svc mongodb-nationalparks", guide)
        self.assertNotIn("oc apply -f clusterextension", guide)
        self.assertIn("name: Gitea", UI_CONFIG.read_text())
        self.assertIn("name: ArgoCD", UI_CONFIG.read_text())

    def test_delivery_preflight_is_for_full_stack_not_single_configmap(self):
        text = INSTRUCTOR.read_text()
        self.assertIn("Auto-Sync", text)
        self.assertIn("Three Deployments", text)
        self.assertIn("Two HTTPS Routes", text)
        self.assertIn("Default StorageClass", text)
        self.assertIn("two", text)
        self.assertNotIn("This workshop intentionally uses **one GitOps-owned ConfigMap**",
                         text)


if __name__ == "__main__":
    unittest.main()
