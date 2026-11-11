"""Module 1: read-only Lightspeed diagnosis and a one-field Service fix."""
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "content/modules/ROOT/pages/module-01-whats-new-in-ocp5.adoc"
INDEX = ROOT / "content/modules/ROOT/pages/index.adoc"

class LightspeedWorkshopTests(unittest.TestCase):
    def test_read_only_prompt(self):
        guide = GUIDE.read_text()
        self.assertIn("OpenShift Lightspeed 2.0", guide)
        self.assertIn("Troubleshooting", guide)
        self.assertIn("Do not read Secrets or change anything.", guide)
        self.assertIn("namespace {user}-demo", guide)

    def test_fault_is_service_selector_not_mongodb_image(self):
        guide = GUIDE.read_text()
        self.assertIn("app: intentionally-broken-backend", guide)
        self.assertIn("== Mission 5: Repair the Service", guide)
        self.assertIn("spec.selector", guide)
        self.assertIn("quay.io/mongodb/mongodb-community-server:8.0.32-ubi9-slim", (ROOT / "content/modules/ROOT/examples/module01-mongodb.yaml").read_text())
        self.assertNotIn("registry.redhat.io/rhmap47/mongodb", guide)
        self.assertNotIn("MongoDB image fix", guide)

    def test_end_to_end_check(self):
        guide = GUIDE.read_text()
        self.assertIn("/ws/data/load", guide)
        self.assertIn("/ws/data/all", guide)
        self.assertIn("/ws/backends/list", guide)

if __name__ == "__main__":
    unittest.main()
