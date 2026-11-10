"""Static contract for the disposable, image-only MongoDB recovery lab.

Run from the repository root with:
    python3 -m unittest discover -s tests -p 'test_module01_mongodb_recovery.py'

This validates the prepared manifest, not image pulls, JavaScript execution,
MongoDB authentication, or the OpenShift Lightspeed write tools.
"""

import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "content/modules/ROOT/examples/module01-mongodb.yaml"
BROKEN_IMAGE = "registry.redhat.io/rhmap47/mongodb"
WORKING_IMAGE = "quay.io/mongodb/mongodb-community-server:8.0.32-ubi9-slim"
SECRET = "nationalparks-mongodb-parameters"


class MongoDBRecoveryManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = MANIFEST.read_text(encoding="utf-8")
        cls.resources = list(yaml.safe_load_all(cls.source))
        cls.by_kind = {resource["kind"]: resource for resource in cls.resources}
        cls.deployment = cls.by_kind["Deployment"]
        cls.container = next(
            c for c in cls.deployment["spec"]["template"]["spec"]["containers"]
            if c["name"] == "mongodb"
        )

    def test_only_three_approved_resources_and_no_secret(self):
        self.assertEqual(set(self.by_kind), {"ConfigMap", "Deployment", "Service"})
        for resource in self.resources:
            self.assertEqual(resource["metadata"]["name"].split("-bootstrap")[0],
                             "mongodb-nationalparks")
            self.assertNotIn("namespace", resource["metadata"])

    def test_starts_broken_without_spoiling_recovery_in_import_yaml(self):
        self.assertEqual(self.container["image"], BROKEN_IMAGE)
        self.assertNotIn(WORKING_IMAGE, self.source)
        self.assertEqual(self.container["imagePullPolicy"], "IfNotPresent")

    def test_modern_root_credentials_are_preconfigured(self):
        self.assertEqual(self.container["envFrom"],
                         [{"secretRef": {"name": SECRET}}])
        environment = {item["name"]: item for item in self.container["env"]}
        self.assertEqual(environment["MONGO_INITDB_ROOT_USERNAME"]["value"],
                         "nationalparks-admin")
        self.assertEqual(
            environment["MONGO_INITDB_ROOT_PASSWORD"]["valueFrom"]["secretKeyRef"],
            {"name": SECRET, "key": "MONGODB_ADMIN_PASSWORD"},
        )
        self.assertEqual(
            environment["MONGO_INITDB_DATABASE"]["valueFrom"]["secretKeyRef"],
            {"name": SECRET, "key": "MONGODB_DATABASE"},
        )

    def test_both_storage_paths_and_user_bootstrap_are_ready(self):
        spec = self.deployment["spec"]["template"]["spec"]
        mounts = {item["name"]: item for item in self.container["volumeMounts"]}
        self.assertEqual(mounts["legacy-data"]["mountPath"],
                         "/var/lib/mongodb/data")
        self.assertEqual(mounts["modern-data"]["mountPath"], "/data/db")
        self.assertEqual(mounts["app-user-bootstrap"]["mountPath"],
                         "/docker-entrypoint-initdb.d")
        self.assertTrue(mounts["app-user-bootstrap"]["readOnly"])
        volumes = {item["name"]: item for item in spec["volumes"]}
        self.assertEqual(volumes["legacy-data"]["emptyDir"], {})
        self.assertEqual(volumes["modern-data"]["emptyDir"], {})
        self.assertEqual(volumes["app-user-bootstrap"]["configMap"]["name"],
                         "mongodb-nationalparks-bootstrap")
        script = self.by_kind["ConfigMap"]["data"]["create-app-user.js"]
        for required in ("process.env.MONGODB_DATABASE", "process.env.MONGODB_USER",
                         "process.env.MONGODB_PASSWORD", "createUser(", "readWrite"):
            self.assertIn(required, script)

    def test_database_service_remains_internal(self):
        service = self.by_kind["Service"]
        self.assertEqual(service["spec"]["type"], "ClusterIP")
        self.assertEqual(service["spec"]["ports"][0]["port"], 27017)
        pod_labels = self.deployment["spec"]["template"]["metadata"]["labels"]
        for label, expected in service["spec"]["selector"].items():
            self.assertEqual(pod_labels[label], expected)


if __name__ == "__main__":
    unittest.main()
