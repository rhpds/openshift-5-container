"""Regression contract for read-only student AgenticOLSConfig access.

The Agentic Runs console reads singleton AgenticOLSConfig/cluster, while its
all-namespace AgenticRun list requires a separate console fix. Do not broaden
student roles to list other students' AgenticRuns.
"""

import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "automation/gitops/bootstrap-tenant/templates/lightspeed-rbac.yaml"


class StudentAgenticConfigRBAC(unittest.TestCase):
    def test_only_singleton_config_is_readable(self):
        rendered = (TEMPLATE.read_text()
                    .replace("{{ .Values.username | quote }}", '"user-abcde"')
                    .replace("{{ .Values.username }}", "user-abcde"))
        objects = list(yaml.safe_load_all(rendered))
        self.assertEqual([obj["kind"] for obj in objects],
                         ["ClusterRoleBinding", "ClusterRole", "ClusterRoleBinding"])

        existing, role, binding = objects
        self.assertEqual(existing["roleRef"]["name"],
                         "lightspeed-operator-query-access")
        self.assertEqual(existing["subjects"][0]["name"], "user-abcde")

        self.assertEqual(role["metadata"]["name"], "user-abcde-agentic-config-viewer")
        self.assertEqual(role["rules"], [{
            "apiGroups": ["agentic.openshift.io"],
            "resources": ["agenticolsconfigs"],
            "resourceNames": ["cluster"],
            "verbs": ["get"],
        }])
        self.assertEqual(binding["metadata"]["name"], role["metadata"]["name"])
        self.assertEqual(binding["subjects"], [{
            "kind": "User",
            "apiGroup": "rbac.authorization.k8s.io",
            "name": "user-abcde",
        }])
        self.assertEqual(binding["roleRef"], {
            "apiGroup": "rbac.authorization.k8s.io",
            "kind": "ClusterRole",
            "name": role["metadata"]["name"],
        })
        self.assertEqual(role["metadata"]["annotations"]["argocd.argoproj.io/sync-wave"], "0")
        self.assertEqual(binding["metadata"]["annotations"]["argocd.argoproj.io/sync-wave"], "0")

        for obj in objects:
            if obj["kind"] != "ClusterRole":
                continue
            for rule in obj["rules"]:
                self.assertNotIn("agenticruns", rule["resources"])
                self.assertNotIn("secrets", rule["resources"])
                self.assertNotIn("list", rule["verbs"])
                self.assertNotIn("watch", rule["verbs"])
                self.assertNotIn("create", rule["verbs"])
                self.assertNotIn("patch", rule["verbs"])
                self.assertNotIn("update", rule["verbs"])


if __name__ == "__main__":
    unittest.main()
