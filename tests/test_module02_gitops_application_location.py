"""Ensure student Argo CD/Application are co-located in pre-created -gitops."""

import re
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from workspace_repo import workspace_root

import yaml

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "automation/gitops/bootstrap-tenant/templates"
EXAMPLE = ROOT / "docs/instructor/applications/national-parks-application-example.yaml"
STUDENT = ROOT / "content/modules/ROOT/pages/module-02-gitops-onboarding-multitenancy.adoc"
BASELINE = workspace_root() / "scripts/prepare-module03-baseline.sh"
MODULE3 = ROOT / "content/modules/ROOT/pages/module-03-agentic-application-operations.adoc"
MODULE4 = ROOT / "content/modules/ROOT/pages/module-04-ai-assisted-incident-investigation.adoc"


class StudentGitOpsLocationTests(unittest.TestCase):
    def test_tenant_workload_provisions_gitops_before_argocd(self):
        controller = (TEMPLATES / "argocd.yaml").read_text()

        # ocp4_workload_tenant_namespace owns the -gitops namespace now.
        for path in TEMPLATES.glob("*.yaml"):
            self.assertNotIn("kind: Namespace", path.read_text(), path.name)

        self.assertIn("kind: ArgoCD", controller)
        self.assertIn("name: argocd", controller)
        self.assertIn("namespace: {{ .Values.username }}-gitops", controller)
        self.assertIn('argocd.argoproj.io/sync-wave: "0"', controller)
        self.assertIn("ocp4_workload_tenant_namespace", controller)
        self.assertNotIn("namespace: {{ .Values.username }}-demo", controller)

    def test_student_namespace_admin_comes_from_tenant_workload(self):
        for name in (
            "module02-student-application-editor.yaml",
            "module02-student-view.yaml",
        ):
            self.assertFalse((TEMPLATES / name).exists(), name)

        preflight = (
            ROOT / "docs/instructor/module-02-gitops-preflight.md"
        ).read_text()
        self.assertIn("ocp4_workload_tenant_namespace", preflight)
        self.assertIn('oc get rolebinding "admin-$USER_NAME"', preflight)
        self.assertNotIn("module02-application-editor", preflight)
        self.assertNotIn("module02-student-view", preflight)

    def test_example_and_student_yaml_are_aligned(self):
        example = yaml.safe_load(EXAMPLE.read_text())
        guide = STUDENT.read_text()
        self.assertEqual(example["metadata"]["namespace"], "user-xtm9x-gitops")
        self.assertEqual(example["spec"]["destination"]["namespace"], "user-xtm9x-gitops")
        self.assertIn('namespace: "{user}-gitops"', guide)
        self.assertIn("automatically provisioned", guide)
        self.assertIn("privileged tenant bootstrap", guide)
        self.assertNotIn("Import YAML", guide)
        self.assertNotIn("kind: Namespace", guide)
        self.assertIn("If it exists in *{user}-demo*", guide)
        self.assertNotIn("module02-application-editor", guide)
        self.assertIn("gitea-{user}-demo.", guide)

    def test_fast_forward_refuses_legacy_duplicate(self):
        script = BASELINE.read_text()
        start = script.index("apply_gitops_application()")
        end = script.index("\nwait_gitops()", start)
        block = script[start:end]
        self.assertIn('oc get application "$APPLICATION" -n "$DEMO_NS"', block)
        self.assertLess(block.index('-n "$DEMO_NS"'), block.index('-n "$GITOPS_NS"'))
        self.assertIn("Legacy $DEMO_NS/$APPLICATION exists", block)
        self.assertIn('oc apply -n "$GITOPS_NS" -f -', block)
        self.assertIn("namespace: $GITOPS_NS", block)
        self.assertNotIn("namespace: $DEMO_NS", block)
        self.assertNotIn("cmp -s", script)
        self.assertIn("git diff --no-index --quiet --", script)

    def test_module3_and_4_point_to_new_application_location(self):
        for path in (MODULE3, MODULE4):
            guide = path.read_text()
            with self.subTest(path=path):
                variable = "ARGOCD_NAMESPACE" if path == MODULE3 else "NS"
                self.assertIn(f'export {variable}="$STUDENT-gitops"', guide)
                self.assertNotIn('export ARGOCD_NAMESPACE="$STUDENT-demo"', guide)
                self.assertIn("national-parks-settings", guide)


if __name__ == "__main__":
    unittest.main()
