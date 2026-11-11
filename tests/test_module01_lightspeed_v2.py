"""Ensure the Module 1 Lightspeed 2.0 workshop contract stays consistent."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "content/modules/ROOT/pages/module-01-whats-new-in-ocp5.adoc"
INDEX = ROOT / "content/modules/ROOT/pages/index.adoc"
PREFLIGHT = ROOT / "docs/instructor/module-01-deployment-preflight.md"


class LightspeedV2WorkshopTests(unittest.TestCase):
    def test_student_troubleshooting_uses_live_reads(self):
        text = MODULE.read_text()
        self.assertIn("OpenShift Lightspeed 2.0", text)
        self.assertIn("select *Troubleshooting*", text)
        self.assertIn("Do not read Secrets or change any resources.", text)
        self.assertIn("No approval popup?", text)
        self.assertIn("approve *only* read actions", text)

    def test_ai_repair_recommendation_is_validated(self):
        text = MODULE.read_text()
        self.assertIn("Ignore unverified image suggestions", text)
        self.assertIn("*AI check:*", text)
        self.assertNotIn("image::module01-s10a-approve-resource-list.png", text)
        self.assertNotIn("image::module01-s10b-approve-pod-list.png", text)
        self.assertNotIn("image::module01-s10c-approve-pod-logs.png", text)

    def test_image_recovery_is_student_applied(self):
        text = MODULE.read_text()
        self.assertIn("== Mission 5: Apply the MongoDB image fix in the console", text)
        self.assertIn("quay.io/mongodb/mongodb-community-server:8.0.32-ubi9-slim", text)
        self.assertIn("the container image was the only field you changed", text)

    def test_recovery_checks_both_api_and_frontend(self):
        text = MODULE.read_text()
        self.assertIn("`/ws/data/all`", text)
        self.assertIn("`/ws/backends/list`", text)
        self.assertIn("*API works but map is empty?*", text)

    def test_overview_and_preflight_do_not_require_mcp_writes(self):
        index = INDEX.read_text()
        preflight = PREFLIGHT.read_text()
        self.assertIn("Lightspeed Operator 2.0", index)
        self.assertIn("manual console repair", index)
        self.assertIn("lightspeed-operator.v2.0.0", preflight)
        self.assertIn("Generic MCP write tools are not required", preflight)


if __name__ == "__main__":
    unittest.main()
