"""Checkout helper for the student workspace repository.

The GitOps manifests are owned by rhpds/openshift-5-container-workspace.
Manifest tests read them from a shallow clone, so this repository does not
keep a second copy that can drift.

Set WORKSPACE_REPO_DIR to an existing checkout to run the suite offline.
"""
import atexit
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO_URL = "https://github.com/rhpds/openshift-5-container-workspace.git"
_NATIONAL_PARKS = Path("national-parks/kustomization.yaml")

_cache = None


def workspace_root() -> Path:
    global _cache
    if _cache is not None:
        return _cache

    override = os.environ.get("WORKSPACE_REPO_DIR")
    if override:
        root = Path(override).expanduser().resolve()
        if not (root / _NATIONAL_PARKS).is_file():
            raise RuntimeError(
                f"WORKSPACE_REPO_DIR={root} has no {_NATIONAL_PARKS}"
            )
        _cache = root
        return _cache

    root = Path(tempfile.mkdtemp(prefix="workspace-repo-"))
    atexit.register(shutil.rmtree, root, True)
    subprocess.run(
        ["git", "clone", "--quiet", "--depth", "1", REPO_URL, str(root)],
        check=True,
    )
    if not (root / _NATIONAL_PARKS).is_file():
        raise RuntimeError(f"{REPO_URL} main is missing {_NATIONAL_PARKS}")
    _cache = root
    return _cache
