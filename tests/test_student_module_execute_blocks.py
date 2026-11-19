"""Ensure every student-facing shell block has a Showroom Execute control."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "content/modules/ROOT/pages"
MODULES = [
    "module-01-whats-new-in-ocp5.adoc",
    "module-02-gitops-onboarding-multitenancy.adoc",
    "module-03-agentic-application-operations.adoc",
    "module-04-ai-assisted-incident-investigation.adoc",
    "module-05-gitops-remediation-app-lifecycle.adoc",
]
EXECUTE = '[source,bash,subs="attributes+",role=execute]'
LOGIN = (
    "oc login --server={openshift_api_url} --username={user} "
    "--password='{password}' --insecure-skip-tls-verify"
)


class StudentExecuteBlockTests(unittest.TestCase):
    def test_all_module_bash_blocks_are_executable(self):
        for module in MODULES:
            with self.subTest(module=module):
                guide = (PAGES / module).read_text()
                headers = re.findall(r"^\[source,bash[^\n]*\]$", guide, re.M)
                self.assertGreater(len(headers), 0)
                self.assertTrue(all(header == EXECUTE for header in headers), headers)

    def test_each_module_has_executable_login(self):
        for module in MODULES:
            with self.subTest(module=module):
                guide = (PAGES / module).read_text()
                self.assertIn(EXECUTE + "\n----\n" + LOGIN, guide)

    def test_overview_login_is_executable(self):
        guide = (PAGES / "index.adoc").read_text()
        self.assertIn(EXECUTE + "\n----\n" + LOGIN + "\noc whoami", guide)

    def test_non_shell_examples_are_not_marked_execute(self):
        for module in MODULES:
            with self.subTest(module=module):
                guide = (PAGES / module).read_text()
                self.assertNotRegex(
                    guide,
                    r"^\[source,(?:yaml|text)[^\n]*role=execute",
                )


if __name__ == "__main__":
    unittest.main()
