"""Every student module starts by logging into OpenShift as the assigned user."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1] / "content/modules/ROOT/pages"
MODULES = (
    "module-01-whats-new-in-ocp5.adoc",
    "module-02-gitops-onboarding-multitenancy.adoc",
    "module-03-agentic-application-operations.adoc",
    "module-04-ai-assisted-incident-investigation.adoc",
    "module-05-gitops-remediation-app-lifecycle.adoc",
)
LOGIN = "oc login --server={openshift_api_url} --username={user} --password='{password}' --insecure-skip-tls-verify"

class ModuleStudentLoginTests(unittest.TestCase):
    def test_every_module_begins_with_student_login(self):
        for filename in MODULES:
            with self.subTest(module=filename):
                doc = (ROOT / filename).read_text()
                self.assertEqual(doc.count(LOGIN), 1, filename)
                section = "== Start here: Log in to OpenShift"
                self.assertEqual(doc.count(section), 1)
                self.assertIn('[source,bash,subs="attributes+",role=execute]', doc)
                # Login appears at the very beginning, before the first mission.
                self.assertLess(doc.index(LOGIN), doc.index("== Mission"))
                self.assertLess(doc.index(section), doc.index(LOGIN))
                self.assertIn("oc whoami", doc)

if __name__ == "__main__":
    unittest.main()
