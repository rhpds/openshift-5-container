"""Validate real Module 3 screenshots and the remaining SVG placeholders."""
from pathlib import Path
import hashlib
import re
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "content/modules/ROOT/pages"
IMAGES = ROOT / "content/modules/ROOT/images"
GUIDES = ROOT / "docs/instructor"
MODULES = (
    (3, "module-03-agentic-application-operations.adoc", 12),
    (4, "module-04-ai-assisted-incident-investigation.adoc", 12),
)
REAL_SCREENSHOTS = {
    "module03-s01-student-deployment-baseline.png": "a7038781a205ae354f3b9d9518405e3b588e64835e92a0f735687bafd4883a62",
    "module03-s02-resource-usage-quotas.png": "fdff433b3d743b5521549fb66819415f8f083553bcc7e8c4f4b6eb346366d251",
    "module03-s03-healthy-routes-endpoints.png": "1f16916bdd0f0fa81c0c30dc1db95553289ebe8fbf1ec900f7f7dc2775146af0",
    "module03-s04-gitea-frontend-source.png": "54b6679e214669d20e39d1809258c31c917a44f6d655d0ad0b8ffc6ef6f4690c",
}

class ScreenshotTests(unittest.TestCase):
    def test_numbered_illustrations_exist_and_are_readable(self):
        for module, page_name, count in MODULES:
            text = (PAGES / page_name).read_text()
            refs = re.findall(
                rf"^image::(module0{module}-s\d{{2}}-[\w-]+\.(?:svg|png))\[([^\]]+)\]$",
                text, flags=re.MULTILINE,
            )
            self.assertEqual(len(refs), count, (module, refs))
            self.assertEqual(len({name for name, _ in refs}), count)
            self.assertEqual(
                [int(re.search(r"-s(\d{2})-", name).group(1)) for name, _ in refs],
                ([1,2,3,4,5,6,7,8,9,10,13,14] if module == 3 else [1,2,3,4,5,6,7,8,9,10,14,15]),
            )
            guide = (GUIDES / f"module-0{module}-screenshot-capture-checklist.md").read_text()
            for index, (name, alt) in enumerate(refs, start=1):
                with self.subTest(module=module, image=name):
                    path = IMAGES / name
                    self.assertTrue(path.is_file(), str(path))
                    self.assertIn(name, guide)
                    self.assertIn("width=850", alt)
                    if module == 3 and index <= 4:
                        self.assertTrue(name.endswith(".png"))
                        self.assertNotIn("screenshot placeholder", alt)
                        blob = path.read_bytes()
                        self.assertTrue(blob.startswith(b"\x89PNG\r\n\x1a\n"))
                        self.assertEqual(hashlib.sha256(blob).hexdigest(), REAL_SCREENSHOTS[name])
                    else:
                        self.assertTrue(name.endswith(".svg"))
                        self.assertIn("screenshot placeholder", alt)
                        data = path.read_text()
                        root = ET.fromstring(data)
                        self.assertTrue(root.tag.endswith("svg"))
                        self.assertIn("SCREENSHOT NEEDED", data)

    def test_real_screenshots_are_exactly_the_four_expected(self):
        self.assertEqual(len(REAL_SCREENSHOTS), 4)
        for filename in REAL_SCREENSHOTS:
            with self.subTest(filename=filename):
                self.assertTrue((IMAGES / filename).is_file())

    def test_no_module02_images_in_other_modules(self):
        for module, page_name, _ in MODULES:
            text = (PAGES / page_name).read_text()
            self.assertNotIn("image::module02-", text)
            self.assertIn(f"module0{module}-s01-", text)

if __name__ == "__main__":
    unittest.main()
