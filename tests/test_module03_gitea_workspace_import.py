"""Module 3 must identify missing student Gitea imports without credential prompts."""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "automation/scripts/prepare-module03-baseline.sh"
MODULE = ROOT / "content/modules/ROOT/pages/module-03-agentic-application-operations.adoc"
INSTRUCTOR = ROOT / "docs/instructor/module03-fast-forward-bootstrap.md"


class Module03WorkspaceImportTests(unittest.TestCase):
    def test_instructor_helper_matches_workspace_repo(self):
        script = SCRIPT.read_text()
        self.assertIn("https://github.com/rhpds/openshift-5-container-workspace.git", script)
        self.assertIn('$GITEA_BASE/$STUDENT/openshift-5-container-workspace.git', script)
        self.assertIn('$GITEA_BASE/api/v1/repos/$STUDENT/openshift-5-container-workspace', script)
        self.assertIn("GIT_TERMINAL_PROMPT=0 git", script)

    def test_student_download_stays_on_canonical_workspace(self):
        module = MODULE.read_text()
        self.assertIn(
            "https://raw.githubusercontent.com/rhpds/openshift-5-container-workspace/"
            "main/scripts/prepare-module03-baseline.sh",
            module,
        )

    def test_instructor_recovery_uses_existing_backfill(self):
        instructor = INSTRUCTOR.read_text()
        self.assertIn("reconcile-gitea-repositories.sh -n user-xxxxx-demo", instructor)
        self.assertIn("reconcile-gitea-repositories.sh -n user-xxxxx-demo --apply", instructor)


if __name__ == "__main__":
    unittest.main()
