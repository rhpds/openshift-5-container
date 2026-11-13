"""Contracts for the primary 45-minute Module 2 full-stack Auto-Sync lab."""

import re
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
        self.assertIn("*GitOps -> Applications*", mission3)
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
        self.assertIn("default StorageClass", text)
        self.assertIn("two", text)
        self.assertNotIn("This workshop intentionally uses **one GitOps-owned ConfigMap**",
                         text)


if __name__ == "__main__":
    unittest.main()
