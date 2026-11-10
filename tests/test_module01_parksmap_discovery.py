"""Validate the isolated, read-only ParksMap backend discovery resources."""

import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "content/modules/ROOT/examples/module01-parksmap-discovery.yaml"
GUIDE = ROOT / "content/modules/ROOT/pages/module-01-whats-new-in-ocp5.adoc"


class ParksMapDiscoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resources = list(yaml.safe_load_all(MANIFEST.read_text()))
        cls.by_kind = {obj["kind"]: obj for obj in cls.resources}

    def test_only_expected_namespace_scoped_resources(self):
        self.assertEqual(set(self.by_kind), {"ServiceAccount", "Role", "RoleBinding"})
        for resource in self.resources:
            self.assertEqual(resource["metadata"]["name"], "parksmap-discovery")
            self.assertNotIn("namespace", resource["metadata"])

    def test_discovery_is_read_only_and_excludes_secrets(self):
        role_rules = self.by_kind["Role"]["rules"]
        by_resource = {resource: rule for rule in role_rules
                       for resource in rule["resources"]}
        self.assertEqual(set(by_resource), {"routes", "services", "endpoints"})
        for resource in ("routes", "services"):
            self.assertEqual(set(by_resource[resource]["verbs"]),
                             {"get", "list", "watch"})
        self.assertEqual(set(by_resource["endpoints"]["verbs"]),
                         {"get", "watch"})
        self.assertEqual(set(by_resource["endpoints"]["resourceNames"]),
                         {"nationalparks", "national-parks-app"})

    def test_binding_and_documentation_use_dedicated_identity(self):
        binding = self.by_kind["RoleBinding"]
        self.assertEqual(binding["roleRef"]["name"], "parksmap-discovery")
        self.assertEqual(binding["subjects"], [{
            "kind": "ServiceAccount", "name": "parksmap-discovery",
            "namespace": "STUDENT_NAMESPACE_REPLACE_ME",
        }])
        guide = GUIDE.read_text()
        self.assertIn("include::example$module01-parksmap-discovery.yaml[]", guide)
        self.assertIn("serviceAccountName: parksmap-discovery", guide)


if __name__ == "__main__":
    unittest.main()
