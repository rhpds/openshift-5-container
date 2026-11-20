"""Student Module 3 contract: measured workload management, not AgenticRun execution."""
import re
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from workspace_repo import workspace_root
import yaml

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "content/modules/ROOT/pages/module-03-agentic-application-operations.adoc"
MODULE4 = ROOT / "content/modules/ROOT/pages/module-04-ai-assisted-incident-investigation.adoc"
INDEX = ROOT / "content/modules/ROOT/pages/index.adoc"
NAV = ROOT / "content/modules/ROOT/nav.adoc"
INSTRUCTOR = ROOT / "docs/instructor/module-03-agentic-app-deployment-preflight.md"
SOURCE = workspace_root() / "national-parks/04-parksmap-frontend.yaml"


class WorkloadManagementTests(unittest.TestCase):
    def test_five_missions_and_25_minutes(self):
        guide = MODULE.read_text()
        self.assertEqual(len(re.findall(r"^== Mission [1-5]:", guide, re.M)), 5)
        self.assertIn("*Estimated time: 25 minutes*", guide)
        self.assertIn("== Completion check", guide)
        for topic in ("ClusterResourceQuota", "AppliedClusterResourceQuota",
                      "oc adm top pods", "Perses", "CPU", "memory",
                      "Gitea", "Synced", "Healthy", "Right-Size"):
            self.assertIn(topic.lower(), guide.lower())
        self.assertNotIn("port: 18080", guide)
        self.assertNotIn("cat <<YAML | oc create", guide)
        self.assertNotIn("oc patch deployment", guide)
        self.assertNotIn("oc create namespace", guide)

    def test_bounded_gitops_sizing_only(self):
        guide = MODULE.read_text()
        self.assertIn('GITOPS_NAMESPACE="$STUDENT-gitops"', guide)
        self.assertIn('ARGOCD_NAMESPACE="$STUDENT-gitops"', guide)
        self.assertIn("04-parksmap-frontend.yaml", guide)
        self.assertIn("75m", guide)
        self.assertIn("50m", guide)
        self.assertIn("100m", guide)
        self.assertIn("192Mi", guide)
        self.assertIn("256Mi", guide)
        self.assertIn("No additional operator installation", guide)
        self.assertIn("AgenticRuns remain *deferred*", guide)
        self.assertIn("no change", guide.lower())
        self.assertIn("oc rollout status deployment/parksmap", guide)
        self.assertNotIn("oc delete ", guide)

    def test_canonical_manifest_healthy_and_unchanged(self):
        objs = list(yaml.safe_load_all(SOURCE.read_text()))
        deployment = next(o for o in objs if o["kind"] == "Deployment")
        container = deployment["spec"]["template"]["spec"]["containers"][0]
        self.assertEqual(container["resources"]["requests"],
                         {"cpu": "75m", "memory": "192Mi"})
        self.assertEqual(container["resources"]["limits"],
                         {"cpu": "500m", "memory": "768Mi"})
        self.assertEqual(container["readinessProbe"]["tcpSocket"]["port"], "http")

    def test_instructor_and_module_handoff(self):
        guide = MODULE.read_text()
        instructor = INSTRUCTOR.read_text()
        self.assertIn("workload-management lab", instructor)
        self.assertIn("no change", instructor.lower())
        self.assertIn("rehearsal shortcut", guide.lower())
        self.assertIn("Continue to Module 4", guide)
        self.assertIn("Workload Management", NAV.read_text())
        self.assertIn("Workload Management", INDEX.read_text())
        self.assertIn("WeatherNow", MODULE4.read_text())


if __name__ == "__main__":
    unittest.main()
