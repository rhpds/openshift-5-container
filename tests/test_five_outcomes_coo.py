"""Curriculum contracts for the five outcomes and instructor-scoped COO/Perses."""
import re
import unittest
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "content/modules/ROOT/pages"
MODULE2 = PAGES / "module-02-gitops-onboarding-multitenancy.adoc"
MODULE3 = PAGES / "module-03-agentic-application-operations.adoc"
MODULE4 = PAGES / "module-04-ai-assisted-incident-investigation.adoc"
MODULE5 = PAGES / "module-05-gitops-remediation-app-lifecycle.adoc"
COO = ROOT / "automation/observability/monitoring-uiplugin.yaml"
PREFLIGHT = ROOT / "docs/instructor/cluster-observability-workshop-preflight.md"


class FiveOutcomeTests(unittest.TestCase):
    def test_network_canary_scope_and_cleanup(self):
        text = MODULE2.read_text()
        heredocs = re.findall(
            r"cat <<'YAML' \| oc apply -n \"\$GITOPS_NAMESPACE\" -f -\n(.*?)\nYAML",
            text, re.S,
        )
        self.assertEqual(len(heredocs), 2)
        objs = [o for heredoc in heredocs for o in yaml.safe_load_all(heredoc)]
        self.assertEqual({o["kind"] for o in objs},
                         {"Deployment", "Service", "NetworkPolicy"})
        policy = next(o for o in objs if o["kind"] == "NetworkPolicy")
        self.assertEqual(policy["spec"]["podSelector"]["matchLabels"],
                         {"app": "workshop-netcheck"})
        self.assertEqual(policy["spec"]["policyTypes"], ["Ingress"])
        self.assertEqual(policy["spec"]["ingress"][0]["from"][0]["podSelector"], {})
        self.assertNotIn("namespaceSelector", policy["spec"]["ingress"][0]["from"][0])
        for obj in objs:
            self.assertNotIn("namespace", obj["metadata"])
        self.assertIn("oc delete networkpolicy workshop-netcheck-ingress", text)
        self.assertIn("oc delete deployment workshop-netcheck", text)
        self.assertIn("same-student cross-namespace", text)
        self.assertIn("cross-student", text)

    def test_workload_and_incident_not_repeated(self):
        m3, m4 = MODULE3.read_text(), MODULE4.read_text()
        self.assertNotIn("port: 18080", m3)
        self.assertIn("port: 18080", m4)
        self.assertIn("oc adm top pods", m3)
        self.assertIn("oc adm top pods", m4)
        self.assertIn("oc logs deployment/weathernow", m4)
        self.assertIn("oc get events", m4)
        self.assertIn("no change", m3.lower())
        self.assertIn("AgenticRuns remain *deferred*", m3)
        self.assertNotIn("cat <<YAML | oc create", m3)

    def test_coo_is_instructor_only_and_perses_enabled(self):
        obj = yaml.safe_load(COO.read_text())
        self.assertEqual(obj["kind"], "UIPlugin")
        self.assertEqual(obj["spec"]["type"], "Monitoring")
        self.assertTrue(obj["spec"]["monitoring"]["perses"]["enabled"])
        self.assertIn("instructor", COO.read_text().lower())
        guide = PREFLIGHT.read_text()
        self.assertIn("30 concurrent students", guide)
        self.assertIn("tenant", guide.lower())
        self.assertIn("not", guide.lower())
        self.assertIn("Perses", guide)

    def test_release_recovery_requires_real_sha_and_route(self):
        guide = MODULE5.read_text()
        self.assertIn("full Git SHA", guide)
        self.assertIn(".status.sync.revision", guide)
        self.assertIn("oc rollout status", guide)
        self.assertIn("ImagePullBackOff", guide)
        self.assertIn("HTTP 200", guide)


if __name__ == "__main__":
    unittest.main()
