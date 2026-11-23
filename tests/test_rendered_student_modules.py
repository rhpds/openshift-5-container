"""Check the student pages generated with the project's Antora playbook."""

import re
import shutil
import subprocess
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "content/modules/ROOT/pages"


class StudentArticle(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_article = False
        self.images = []
        self.text = []

    def handle_starttag(self, tag, attrs):
        if tag == "article":
            self.in_article = True
        elif self.in_article and tag == "img":
            self.images.append(dict(attrs)["src"])

    def handle_endtag(self, tag):
        if tag == "article":
            self.in_article = False

    def handle_data(self, data):
        if self.in_article:
            self.text.append(data)


class RenderedStudentModules(unittest.TestCase):
    @unittest.skipUnless(shutil.which("antora"), "requires the Antora CLI and site extensions")
    def test_images_and_student_attributes_in_rendered_articles(self):
        sources = sorted(PAGES.glob("module-0[1-5]-*.adoc"))
        self.assertEqual(len(sources), 5)
        with tempfile.TemporaryDirectory() as output:
            subprocess.run(
                ["antora", "--attribute", "user=student-render-check", "--to-dir", output, "site.yml"],
                cwd=ROOT, check=True,
            )
            for source in sources:
                with self.subTest(module=source.stem):
                    page = Path(output) / "modules" / (source.stem + ".html")
                    article = StudentArticle()
                    article.feed(page.read_text())
                    article.close()
                    text = "".join(article.text)
                    self.assertIn("student-render-check", text)
                    self.assertNotIn("{user}", text)
                    self.assertNotIn("image::", text)
                    expected = re.findall(r"^image::([^\s\[]+)\[", source.read_text(), re.MULTILINE)
                    self.assertCountEqual(expected, [Path(src).name for src in article.images])
                    for src in article.images:
                        self.assertTrue((page.parent / src).is_file(), src)
