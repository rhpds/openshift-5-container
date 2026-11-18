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
    def test_bootstrap_creates_namespace_before_argocd(self):
        namespace = (TEMPLATES / "module02-namespace.yaml").read_text()
        controller = (TEMPLATES / "argocd.yaml").read_text()

        self.assertIn("kind: Namespace", namespace)
        self.assertIn("name: {{ .Values.username }}-gitops", namespace)
        self.assertIn('argocd.argoproj.io/sync-wave: "-1"', namespace)
        self.assertIn("openshift.io/requester:", namespace)
        self.assertNotIn("argocd.argoproj.io/managed-by:", namespace)

        self.assertIn("kind: ArgoCD", controller)
        self.assertIn("name: argocd", controller)
        self.assertIn("namespace: {{ .Values.username }}-gitops", controller)
        self.assertIn('argocd.argoproj.io/sync-wave: "0"', controller)
        self.assertNotIn("namespace: {{ .Values.username }}-demo", controller)

    def test_student_can_edit_only_application_cr(self):
        rbac = (TEMPLATES / "module02-student-application-editor.yaml").read_text()
        objects = list(yaml.safe_load_all(
            rbac.replace("{{ .Values.username | quote }}", '"user-xxxxx"')
                .replace("{{ .Values.username }}", "user-xxxxx")
        ))
        self.assertEqual([o["kind"] for o in objects], ["Role", "RoleBinding"])
        role, binding = objects
        self.assertEqual(role["metadata"]["namespace"], "user-xxxxx-gitops")
        self.assertEqual(binding["metadata"]["namespace"], "user-xxxxx-gitops")
        self.assertEqual(role["rules"], [{
            "apiGroups": ["argoproj.io"],
            "resources": ["applications"],
            "verbs": ["get", "list", "watch", "create", "update", "patch"],
        }])
        self.assertEqual(binding["subjects"][0]["name"], "user-xxxxx")
        self.assertEqual(binding["roleRef"]["name"], role["metadata"]["name"])

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
        self.assertIn("module02-application-editor", guide)
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
                self.assertIn('export ARGOCD_NAMESPACE="$STUDENT-gitops"', guide)
                self.assertNotIn('export ARGOCD_NAMESPACE="$STUDENT-demo"', guide)
                self.assertIn("national-parks-settings", guide)


if __name__ == "__main__":
    unittest.main()
