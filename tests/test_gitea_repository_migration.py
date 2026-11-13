"""Tests for the namespaced, dry-run-by-default Gitea backfill helper."""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "automation/scripts/reconcile-gitea-repositories.sh"

MOCK_OC = r'''#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
p = Path(os.environ["MOCK_GITEA_STATE"])
state = json.loads(p.read_text())
args = sys.argv[1:]
if args[0] == "get":
    print(json.dumps(state["cr"]))
elif args[0] == "patch":
    change = json.loads(args[args.index("-p") + 1])
    if "--subresource=status" in args:
        state["cr"]["status"].update(change["status"])
    else:
        state["cr"]["spec"].update(change["spec"])
        if change["spec"].get("giteaMigrateRepositories") is True:
            state["imported"] = True
            state["cr"]["status"]["repoMigrationComplete"] = True
    state["patches"].append(change)
    p.write_text(json.dumps(state))
    print("gitea.pfe.rhpds.com/gitea patched")
else:
    sys.exit("unexpected oc command")
'''

MOCK_CURL = r'''#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
state = json.loads(Path(os.environ["MOCK_GITEA_STATE"]).read_text())
url = sys.argv[-1]
if url.endswith("/openshift-starter-guides"):
    print("200", end="")
elif url.endswith("/openshift-5-container"):
    print("200" if state["imported"] else "404", end="")
else:
    print("404", end="")
'''


class GiteaBackfillTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.directory = Path(tmp.name)
        self.state_path = self.directory / "state.json"
        self.state_path.write_text(json.dumps({
            "imported": False,
            "patches": [],
            "cr": {
                "spec": {
                    "giteaCreateUsers": True,
                    "giteaMigrateRepositories": True,
                    "giteaUserNumber": 1,
                    "giteaGenerateUserFormat": "user-6k7ww",
                    "giteaRepositoriesList": [
                        {"name": "openshift-starter-guides", "private": False},
                        {"name": "openshift-5-container", "private": False}
                    ],
                },
                "status": {
                    "adminPassword": "mock-secret-never-display",
                    "userSetupComplete": True,
                    "repoMigrationComplete": True,
                    "giteaRoute": "https://gitea.example.test",
                },
            },
        }))
        for name, content in [("oc", MOCK_OC), ("curl", MOCK_CURL)]:
            path = self.directory / name
            path.write_text(content)
            path.chmod(0o755)
        self.env = dict(os.environ)
        self.env["MOCK_GITEA_STATE"] = str(self.state_path)
        self.env["PATH"] = str(self.directory) + os.pathsep + os.environ["PATH"]

    def run_script(self, *args):
        return subprocess.run(
            ["bash", str(SCRIPT), "-n", "user-6k7ww-demo", *args],
            env=self.env, text=True, capture_output=True, timeout=20
        )

    def test_bash_syntax(self):
        r = subprocess.run(["bash", "-n", str(SCRIPT)], capture_output=True)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_dry_run_detects_missing_without_patching(self):
        r = self.run_script()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("MISSING user-6k7ww/openshift-5-container", r.stdout)
        self.assertIn("DRY RUN", r.stdout)
        self.assertNotIn("mock-secret-never-display", r.stdout)
        self.assertEqual(json.loads(self.state_path.read_text())["patches"], [])

    def test_apply_retriggers_and_verifies(self):
        r = self.run_script("--apply")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("SUCCESS", r.stdout)
        state = json.loads(self.state_path.read_text())
        self.assertTrue(state["imported"])
        self.assertTrue(state["cr"]["status"]["repoMigrationComplete"])
        self.assertEqual(state["patches"], [
            {"status": {"repoMigrationComplete": False}},
            {"spec": {"giteaMigrateRepositories": False}},
            {"spec": {"giteaMigrateRepositories": True}},
        ])

    def test_noop_if_both_repositories_exist(self):
        state = json.loads(self.state_path.read_text())
        state["imported"] = True
        self.state_path.write_text(json.dumps(state))
        r = self.run_script("--apply")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("no changes made", r.stdout)
        self.assertEqual(json.loads(self.state_path.read_text())["patches"], [])

    def test_refuse_private_repository(self):
        state = json.loads(self.state_path.read_text())
        state["cr"]["spec"]["giteaRepositoriesList"][1]["private"] = True
        self.state_path.write_text(json.dumps(state))
        r = self.run_script("--apply")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("Private repository", r.stderr)
        self.assertEqual(json.loads(self.state_path.read_text())["patches"], [])


if __name__ == "__main__":
    unittest.main()
