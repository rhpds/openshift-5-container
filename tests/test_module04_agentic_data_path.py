"""Contract tests for Module 4's student-owned, safe National Parks incident."""

from pathlib import Path
import re
import subprocess
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "content/modules/ROOT/pages/module-04-ai-assisted-incident-investigation.adoc"
MANIFEST = ROOT / "content/modules/ROOT/examples/module02-gitops/fullstack/02-nationalparks-backend.yaml"
MONGODB = ROOT / "content/modules/ROOT/examples/module02-gitops/fullstack/01-mongodb.yaml"
MODULE3 = ROOT / "content/modules/ROOT/pages/module-03-agentic-application-operations.adoc"
MODULE5 = ROOT / "content/modules/ROOT/pages/module-05-gitops-remediation-app-lifecycle.adoc"
INDEX = ROOT / "content/modules/ROOT/pages/index.adoc"
NAV = ROOT / "content/modules/ROOT/nav.adoc"
INSTRUCTOR = ROOT / "docs/instructor/module-04-agentic-data-path-preflight.md"
SCRIPT = ROOT / "automation/scripts/create-module04-agentic-run.sh"


class Module04AgenticDataPathTests(unittest.TestCase):
    def test_five_missions_and_three_knowledge_checks(self):
        guide = GUIDE.read_text()
        missions = re.findall(r"^== Mission [1-5]:", guide, flags=re.MULTILINE)
        self.assertEqual(len(missions), 5, missions)
        self.assertIn("*Estimated duration: 40 minutes*", guide)
        self.assertEqual(guide.count("[%collapsible]"), 3)
        for word in (
            "Gitea", "AgenticRun", "Lightspeed", "Troubleshooting",
            "MongoDB", "envFrom", "DATABASE_SERVICE_NAME",
            "mongodb-national-parks", "mongodb-nationalparks",
            "Synced / Healthy", "/ws/data/all", "/ws/healthz/",
            'tcpSocket.port: "http"', "Module 3", "Module 5",
        ):
            with self.subTest(word=word):
                self.assertIn(word, guide)
        for section in ("== Troubleshooting", "== Completion check", "== References"):
            self.assertIn(section, guide)

    def test_baseline_is_healthy_and_the_injection_is_documentation_only(self):
        parts = list(yaml.safe_load_all(MANIFEST.read_text()))
        deployment = next(
            obj for obj in parts
            if obj.get("kind") == "Deployment"
            and obj["metadata"]["name"] == "nationalparks"
        )
        container = deployment["spec"]["template"]["spec"]["containers"][0]
        self.assertEqual(container["name"], "nationalparks")
        self.assertEqual(
            container["envFrom"],
            [{"secretRef": {"name": "nationalparks-mongodb-parameters"}}],
        )
        self.assertFalse(any(
            entry.get("name") == "DATABASE_SERVICE_NAME"
            for entry in container.get("env", [])
        ))
        self.assertEqual(
            container["readinessProbe"]["httpGet"]["path"],
            "/ws/healthz/",
        )
        self.assertEqual(container["resources"]["limits"]["memory"], "384Mi")

        services = [
            obj for obj in yaml.safe_load_all(MONGODB.read_text())
            if isinstance(obj, dict) and obj.get("kind") == "Service"
        ]
        self.assertEqual(len(services), 1)
        self.assertEqual(services[0]["metadata"]["name"], "mongodb-nationalparks")
        self.assertEqual(services[0]["spec"]["ports"][0]["port"], 27017)

        guide = GUIDE.read_text()
        self.assertIn("value: mongodb-national-parks", guide)
        self.assertIn("Remove *exactly*", guide)
        self.assertIn("The existing +envFrom.secretRef+ remains intact", guide)

    def test_scope_and_recovery_are_student_gitops_only(self):
        guide = GUIDE.read_text()
        self.assertIn('LAB_NAMESPACE="$STUDENT-demo"', guide)
        self.assertIn('GITOPS_NAMESPACE="$STUDENT-gitops"', guide)
        self.assertIn('ARGOCD_NAMESPACE="$STUDENT-demo"', guide)
        self.assertIn("national-parks-settings", guide)
        self.assertIn(
            "content/modules/ROOT/examples/module02-gitops/fullstack/02-nationalparks-backend.yaml",
            guide,
        )
        self.assertIn("Do not change MongoDB, Secret values, PVCs", guide)
        self.assertIn("Do not manually Sync", guide)
        self.assertIn("Do not change the Secret", guide)
        self.assertIn("No automatic execution", guide)
        self.assertIn("not available/not authorized", guide)
        self.assertIn("--sync-gitea", guide)
        self.assertIn('curl -fsS --max-time 25 "https://$API_HOST/ws/data/all"', guide)
        self.assertIn("fix(module04): remove wrong National Parks database hostname override", guide)

    def test_instructor_agenticrun_is_guarded_and_analysis_only(self):
        script = SCRIPT.read_text()
        subprocess.run(["bash", "-n", str(SCRIPT)], check=True)
        help_text = subprocess.run(
            ["bash", str(SCRIPT), "--help"],
            check=True, capture_output=True, text=True,
        ).stdout
        self.assertIn("analysis-only AgenticRun", help_text)
        self.assertIn("DATABASE_SERVICE_NAME=mongodb-national-parks", help_text)
        for token in (
            'target_namespace="$student-gitops"',
            'run_name="parksdata-$student-dns"',
            "oc get crd agenticruns.agentic.openshift.io",
            "oc auth can-i create",
            "oc auth can-i get",
            "oc get agent default -o name",
            "if [[ \"$bad_host\" != mongodb-national-parks ]]",
            "oc get service mongodb-nationalparks",
            "cat <<YAML | oc create -f -",
            "No execution or verification stage was configured",
        ):
            with self.subTest(token=token):
                self.assertIn(token, script)

        yaml_text = script.split("cat <<YAML | oc create -f -\n", 1)[1]
        yaml_text = yaml_text.split("\nYAML\n", 1)[0]
        cr = yaml.safe_load(yaml_text)
        self.assertEqual(cr["kind"], "AgenticRun")
        self.assertEqual(cr["apiVersion"], "agentic.openshift.io/v1alpha1")
        self.assertEqual(cr["metadata"]["namespace"], "$operator_namespace")
        self.assertEqual(cr["spec"]["analysis"], {"agent": "default"})
        self.assertNotIn("execution", cr["spec"])
        self.assertNotIn("verification", cr["spec"])
        self.assertNotIn("oc get secret", script)
        self.assertNotIn("oc patch ", script)
        self.assertNotIn("oc scale ", script)
        self.assertNotIn("oc delete ", script)

    def test_instructor_preflight_and_fallback(self):
        doc = INSTRUCTOR.read_text()
        for token in (
            "Agent/default", "AgenticRun", "analysis-only",
            "envFrom", "Secret", "user-<guid>-gitops", "user-<guid>-demo",
            "one run at a time", "readiness", "Module 3",
            "Gitea", "Do not run fast-forward --sync-gitea",
            "No data reset/seed request is required",
        ):
            with self.subTest(token=token):
                self.assertIn(token, doc)

    def test_workshop_links_and_follow_on_warning(self):
        self.assertIn("xref:module-03-agentic-application-operations.adoc", GUIDE.read_text())
        self.assertIn("xref:module-05-gitops-remediation-app-lifecycle.adoc", GUIDE.read_text())
        self.assertIn("Agentic Data-Path Investigation", INDEX.read_text())
        self.assertIn("Agentic Data-Path Investigation", NAV.read_text())
        self.assertIn("Module 3", MODULE3.read_text())
        self.assertIn("Module 5 requires adaptation to the updated GitOps workshop", MODULE5.read_text())
        self.assertIn("already repaired it through student Gitea", MODULE5.read_text())


if __name__ == "__main__":
    unittest.main()
