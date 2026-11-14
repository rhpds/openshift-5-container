"""Ensure each Module 3/4 student screenshot placeholder and image reference is valid."""
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "content/modules/ROOT/pages"
IMAGES = ROOT / "content/modules/ROOT/images"
GUIDES = ROOT / "docs/instructor"
MODULES = (
    (3, "module-03-agentic-application-operations.adoc", 14),
    (4, "module-04-ai-assisted-incident-investigation.adoc", 15),
)

class ScreenshotPlaceholderTests(unittest.TestCase):
    def test_numbered_illustrations_exist_and_are_readable(self):
        for module, page_name, count in MODULES:
            text = (PAGES / page_name).read_text()
            refs = re.findall(
                rf"^image::(module0{module}-s\\d{{2}}-[\\w-]+\\.svg)\\[([^\\]]+)\\]$",
                text, flags=re.MULTILINE)
            self.assertEqual(len(refs), count, (module, refs))
            self.assertEqual(len({name for name, _ in refs}), count)
            self.assertEqual(
                [int(re.search(r"-s(\\d{{2}})-", name).group(1)) for name, _ in refs],
                list(range(1, count + 1)))
            guide = (GUIDES / f"module-0{module}-screenshot-capture-checklist.md").read_text()
            for name, alt in refs:
                with self.subTest(module=module, image=name):
                    self.assertIn("screenshot placeholder", alt)
                    self.assertIn("width=850", alt)
                    self.assertIn(name, guide)
                    path = IMAGES / name
                    self.assertTrue(path.exists(), str(path))
                    data = path.read_text()
                    root = ET.fromstring(data)
                    self.assertTrue(root.tag.endswith("svg"))
                    self.assertIn("SCREENSHOT NEEDED", data)
                    self.assertIn(name.replace(".svg", ".png"), data)

    def test_no_placeholder_for_original_module2_references(self):
        # Modules 1/2 already have a separate screenshot workflow.
        for module, page_name, _ in MODULES:
            text = (PAGES / page_name).read_text()
            self.assertNotIn("image::module02-", text)
            self.assertIn(f"module0{module}-s01-", text)

if __name__ == "__main__":
    unittest.main()
