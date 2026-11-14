#!/usr/bin/env bash
# Module 4 instructor-only, analysis-only data-path AgenticRun.
# No alert policy, credentials, cluster quota or app resources are changed.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: bash automation/scripts/create-module04-agentic-run.sh user-<guid>

Starts one analysis-only AgenticRun for the GitOps National Parks backend
database DNS incident, in openshift-lightspeed. The student first commits
the explicit DATABASE_SERVICE_NAME=mongodb-national-parks override to Gitea.
The script validates the live Deployment and Agentic preflight. It creates
no execution or verification stages and never changes app Deployments.
EOF
}

if [[ $# -eq 1 && ( "$1" == "--help" || "$1" == "-h" ) ]]; then
  usage
  exit 0
fi
if [[ $# -ne 1 || ! "$1" =~ ^user-[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  usage >&2
  exit 2
fi

student="$1"
target_namespace="$student-gitops"
operator_namespace="openshift-lightspeed"
run_name="parksdata-$student-dns"
command -v oc >/dev/null || { echo "oc client required." >&2; exit 1; }
command -v python3 >/dev/null || { echo "python3 required for non-sensitive field inspection." >&2; exit 1; }

if [[ $(printf '%s' "$run_name" | wc -c) -gt 63 ]]; then
  echo "Generated AgenticRun name too long: $run_name" >&2
  exit 2
fi
if ! oc get namespace "$target_namespace" -o name >/dev/null 2>&1; then
  echo "Target namespace unavailable: $target_namespace" >&2
  exit 1
fi
if ! oc get crd agenticruns.agentic.openshift.io -o name >/dev/null 2>&1; then
  echo "AgenticRun CRD not installed/visible. Use read-only CLI and Lightspeed." >&2
  exit 1
fi
if [[ "$(oc auth can-i create agenticruns.agentic.openshift.io -n "$operator_namespace" 2>/dev/null)" != yes ]]; then
  echo "Not authorized to create AgenticRuns in $operator_namespace." >&2
  exit 1
fi
if [[ "$(oc auth can-i get agenticruns.agentic.openshift.io -n "$operator_namespace" 2>/dev/null)" != yes ]]; then
  echo "Not authorized to inspect AgenticRuns in $operator_namespace." >&2
  exit 1
fi
if ! oc get agent default -o name >/dev/null 2>&1; then
  echo "Agent/default not installed or visible; preflight agentic provider." >&2
  exit 1
fi

# Inspect only the non-sensitive explicit env name/value of this Deployment.
# Never read Secrets or print envFrom Secret contents.
bad_host="$(oc get deployment nationalparks -n "$target_namespace" -o json |
  python3 -c 'import json,sys
o=json.load(sys.stdin)
containers=o["spec"]["template"]["spec"]["containers"]
vals=[e.get("value","") for c in containers if c.get("name")=="nationalparks"
      for e in c.get("env",[]) if e.get("name")=="DATABASE_SERVICE_NAME"]
print(vals[0] if len(vals)==1 else "")'
)" || {
  echo "Cannot inspect nationalparks Deployment in $target_namespace." >&2
  exit 1
}
if [[ "$bad_host" != mongodb-national-parks ]]; then
  echo "Refusing run: Module 4 wrong-host override not present in $target_namespace." >&2
  echo "Observed explicit DATABASE_SERVICE_NAME: '$bad_host' (expected mongodb-national-parks)." >&2
  exit 1
fi
if ! oc get service mongodb-nationalparks -n "$target_namespace" -o name >/dev/null 2>&1; then
  echo "Real MongoDB Service missing; this is not the intended Module 4 fault." >&2
  exit 1
fi

if oc get agenticrun "$run_name" -n "$operator_namespace" -o name >/dev/null 2>&1; then
  echo "A run already exists: $operator_namespace/$run_name"
  echo "oc get agenticrun $run_name -n $operator_namespace -o yaml"
  exit 0
fi

cat <<YAML | oc create -f -
apiVersion: agentic.openshift.io/v1alpha1
kind: AgenticRun
metadata:
  name: $run_name
  namespace: $operator_namespace
  labels:
    app.kubernetes.io/part-of: national-parks-module04
    workshop-student: $student
spec:
  request: >-
    Analyze the National Parks Python data-path failure in namespace
    $target_namespace. Deployment/nationalparks may be Ready and GitOps
    Application national-parks-settings in namespace $student-demo may
    report Synced and Healthy, but /ws/data/all no longer returns parks.
    Deployment/mongodb-nationalparks and its Service should be healthy.
    Inspect Kubernetes Deployment non-secret explicit env and envFrom
    reference names, Pod readiness, recent backend logs, the MongoDB
    Service name/port and namespace-local DNS evidence when permitted.
    Explain the precedence of explicit DATABASE_SERVICE_NAME over envFrom,
    and why /ws/healthz/ can pass when MongoDB DNS resolution fails.
    Provide a minimal diagnosis and propose removing the wrong hostname
    override from the student's Gitea source. Do not read Secret data.
    Do not patch, apply, exec untrusted commands, create, delete, scale
    or otherwise modify any Kubernetes resource. Report missing tool
    permissions honestly; do not inspect other student namespaces.
  analysis:
    agent: default
YAML

echo "Created analysis-only AgenticRun $operator_namespace/$run_name"
echo "No execution or verification stage was configured."
echo "Inspect: oc get agenticrun $run_name -n $operator_namespace -o yaml"
echo "No automatic remediation: student repairs the Gitea source."
