"""WeatherNow Module 4/5 and analysis-only AgenticRun contracts."""
import re
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from workspace_repo import workspace_root
import xml.etree.ElementTree as ET
import yaml

ROOT=Path(__file__).resolve().parents[1]
EXAMPLES=workspace_root()/"weathernow"
PAGES=ROOT/"content/modules/ROOT/pages"
IMAGES=ROOT/"content/modules/ROOT/images"
INSTR=ROOT/"docs/instructor"
VALUES=ROOT/"automation/gitops/bootstrap-tenant/values.yaml"
RBAC=ROOT/"automation/gitops/bootstrap-tenant/templates/module04-agenticrun-student-editor.yaml"
ADMISSION=ROOT/"automation/agentic/student-agenticrun-admission.yaml"
SETUP=workspace_root()/"scripts/setup-weathernow-gitops.sh"

class WeatherNowTests(unittest.TestCase):
    def test_minimal_deployment(self):
        objs=list(yaml.safe_load_all((EXAMPLES/"weathernow.yaml").read_text()))
        self.assertEqual([x["kind"] for x in objs],["Deployment","Service","Route"])
        deployment=objs[0]
        container=deployment["spec"]["template"]["spec"]["containers"][0]
        self.assertEqual(container["image"],"quay.io/openshift-workshop-applications/weathernow:latest")
        self.assertEqual(container["ports"][0]["containerPort"],8080)
        self.assertEqual(container["readinessProbe"]["tcpSocket"]["port"],"http")
        self.assertEqual(container["resources"]["limits"],{"cpu":"200m","memory":"128Mi"})
        self.assertEqual(objs[1]["spec"]["ports"][0]["targetPort"],"http")
        self.assertEqual(objs[2]["spec"]["to"]["name"],"weathernow")
        self.assertEqual(yaml.safe_load((EXAMPLES/"kustomization.yaml").read_text())["resources"],["weathernow.yaml"])

    def test_independent_gitops_app(self):
        app=yaml.safe_load((ROOT/"docs/instructor/applications/weathernow-application-example.yaml").read_text())
        self.assertEqual(app["metadata"]["namespace"],"user-xxxxx-gitops")
        self.assertEqual(app["spec"]["destination"]["namespace"],"user-xxxxx-gitops")
        self.assertEqual(app["spec"]["source"]["path"],"weathernow")
        self.assertTrue(app["spec"]["syncPolicy"]["automated"]["selfHeal"])

    def test_student_source_never_overwritten(self):
        s=SETUP.read_text()
        self.assertIn('if [[ -e "$WORK/repo/$SOURCE/$file" ]]',s)
        self.assertIn("Preserving existing",s)
        self.assertIn("oc auth can-i create applications.argoproj.io",s)
        self.assertIn('oc create -n "$GITOPS_NS" -f -',s)
        self.assertNotIn("oc delete ",s)
        self.assertNotIn("git push --force",s)

    def test_student_agenticruns_are_analysis_only(self):
        # Students create runs through namespace admin granted by
        # ocp4_workload_tenant_namespace; the chart no longer grants RBAC.
        self.assertNotIn("agenticStudent", VALUES.read_text())
        self.assertFalse(RBAC.exists())
        policy=list(yaml.safe_load_all(ADMISSION.read_text()))
        self.assertEqual([p["kind"] for p in policy],
          ["ValidatingAdmissionPolicy","ValidatingAdmissionPolicyBinding"])
        checks=policy[0]["spec"]["validations"]
        self.assertTrue(any("execution" in x["expression"] for x in checks))
        self.assertTrue(any("targetCluster" in x["expression"] for x in checks))
        self.assertEqual(policy[1]["spec"]["validationActions"],["Deny"])

    def test_five_missions_and_screenshots(self):
        for module,total in [(4,15),(5,12)]:
            name=("module-04-ai-assisted-incident-investigation.adoc"
                 if module==4 else "module-05-gitops-remediation-app-lifecycle.adoc")
            text=(PAGES/name).read_text()
            self.assertEqual(len(re.findall(r"^== Mission [1-5]:",text,re.M)),5)
            refs=re.findall(rf"^image::(module0{module}-s\d{{2}}-weather-[\w-]+\.svg)\[",text,re.M)
            self.assertEqual(len(refs),total)
            self.assertEqual(len(set(refs)),total)
            checklist=(INSTR/f"module-0{module}-screenshot-capture-checklist.md").read_text()
            for index,filename in enumerate(refs):
                with self.subTest(module=module,file=filename):
                    self.assertIn(f"-s{index+1:02d}-",filename)
                    self.assertIn(filename,checklist)
                    ET.fromstring((IMAGES/filename).read_text())
            self.assertIn("weathernow:latest",text)
            self.assertIn("oc auth can-i create agenticruns.agentic.openshift.io",text)
            self.assertIn("analysis:",text)
            self.assertNotIn("  execution:",text)
            self.assertNotIn("  verification:",text)

if __name__=="__main__":
    unittest.main()
