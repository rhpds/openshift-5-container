"""Contract: Module 4 is the separate lightweight WeatherNow exercise."""
import re
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from workspace_repo import workspace_root
import yaml

ROOT=Path(__file__).resolve().parents[1]
GUIDE=ROOT/"content/modules/ROOT/pages/module-04-ai-assisted-incident-investigation.adoc"
SOURCE=workspace_root()/"weathernow"
MODULE3=ROOT/"content/modules/ROOT/pages/module-03-agentic-application-operations.adoc"
MODULE5=ROOT/"content/modules/ROOT/pages/module-05-gitops-remediation-app-lifecycle.adoc"
INSTRUCTOR=ROOT/"docs/instructor/module-04-agentic-data-path-preflight.md"

class WeatherNowModule04Tests(unittest.TestCase):
    def test_five_missions_and_clear_scope(self):
        text=GUIDE.read_text()
        self.assertEqual(len(re.findall(r"^== Mission [1-5]:",text,re.M)),5)
        self.assertIn("*Duration: 40 minutes*",text)
        self.assertIn("quay.io/openshift-workshop-applications/weathernow:latest",text)
        self.assertIn("weathernow/weathernow.yaml",text)
        self.assertIn("port: 18080",text)
        self.assertIn("port: http",text)
        self.assertIn('NS="$STUDENT-gitops"',text)
        self.assertIn("Student AgenticRuns remain *deferred*", MODULE3.read_text())
        self.assertIn("Validate the WeatherNow readiness diagnosis",text)
        self.assertNotIn("cat <<YAML | oc create",text)
        self.assertIn("No student AgenticRun, extra RBAC or approval is required",text)
        self.assertIn("National Parks",text)
        self.assertIn("oc adm top pods",text)
        self.assertIn("pod-specific +oc logs+",text)
        self.assertNotIn("DATABASE_SERVICE_NAME",text)
    def test_canonical_gitops_source_healthy(self):
        objs=list(yaml.safe_load_all((SOURCE/"weathernow.yaml").read_text()))
        deployment=objs[0]
        self.assertEqual(deployment["kind"],"Deployment")
        container=deployment["spec"]["template"]["spec"]["containers"][0]
        self.assertEqual(container["readinessProbe"]["tcpSocket"]["port"],"http")
        self.assertEqual(container["ports"][0]["containerPort"],8080)
        self.assertEqual(container["resources"]["limits"]["memory"],"128Mi")
    def test_handoff_and_instructor(self):
        self.assertIn("weathernow",MODULE5.read_text().lower())
        self.assertIn("WeatherNow",INSTRUCTOR.read_text())
        self.assertIn("agentic-student-isolation-gate.md",INSTRUCTOR.read_text())

if __name__=="__main__":
    unittest.main()
