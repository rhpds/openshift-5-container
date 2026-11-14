#!/usr/bin/env bash
# Instructor-only on-demand, analysis-only AgenticRun for Module 3.
# Never changes ApprovalPolicy, alert routing, workload resources or Secrets.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: bash automation/scripts/create-module03-agentic-run.sh user-<guid>

Creates ONE analysis-only AgenticRun in openshift-lightspeed for a student's
existing, deliberately misconfigured GitOps ParksMap deployment.
Prerequisites: AgenticRun CRD, Agent/default, instructor RBAC, and
readinessProbe.tcpSocket.port == 18080 in user-<guid>-gitops.
It does NOT configure cluster-wide alerts or permit automated execution.
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
run_name="parksmap-$student-readiness"

# The resource name must be valid for all supported workshop user IDs.
if [[ $(printf '%s' "$run_name" | wc -c) -gt 63 ]]; then
  echo "AgenticRun name is too long: $run_name" >&2
  exit 2
fi

command -v oc >/dev/null || { echo "oc client not installed." >&2; exit 1; }

if ! oc get namespace "$target_namespace" -o name >/dev/null 2>&1; then
  echo "Missing student GitOps namespace: $target_namespace" >&2
  exit 1
fi
if ! oc get crd agenticruns.agentic.openshift.io -o name >/dev/null 2>&1; then
  echo "AgenticRun CRD not installed or not visible; use Lightspeed/CLI investigation." >&2
  exit 1
fi
if [[ "$(oc auth can-i create agenticruns.agentic.openshift.io -n "$operator_namespace" 2>/dev/null)" != "yes" ]]; then
  echo "Current user is not authorized to create AgenticRuns in $operator_namespace." >&2
  exit 1
fi
if [[ "$(oc auth can-i get agenticruns.agentic.openshift.io -n "$operator_namespace" 2>/dev/null)" != "yes" ]]; then
  echo "Current user must be able to inspect their AgenticRun after creation." >&2
  exit 1
fi
if ! oc get agent default -n "$operator_namespace" -o name >/dev/null 2>&1; then
  echo "Agent/default unavailable. Check Agentic Operator readiness and configuration." >&2
  exit 1
fi

# Prevent accidental runs on healthy student apps or the wrong namespace.
live_probe_port="$(oc get deployment parksmap -n "$target_namespace" \
  -o jsonpath='{.spec.template.spec.containers[0].readinessProbe.tcpSocket.port}' 2>/dev/null || true)"
if [[ "$live_probe_port" != "18080" ]]; then
  echo "Expected deliberate Module 3 fault (ParksMap readiness port 18080) in" >&2
  echo "$target_namespace, but found '$live_probe_port'. Do not create a run." >&2
  exit 1
fi

if oc get agenticrun "$run_name" -n "$operator_namespace" -o name >/dev/null 2>&1; then
  echo "Existing run: $operator_namespace/$run_name"
  echo "Inspect it instead of creating a duplicate:"
  echo "  oc get agenticrun $run_name -n $operator_namespace -o yaml"
  exit 0
fi

cat <<YAML | oc create -f -
apiVersion: agentic.openshift.io/v1alpha1
kind: AgenticRun
metadata:
  name: $run_name
  namespace: $operator_namespace
  labels:
    app.kubernetes.io/part-of: national-parks-module03
    workshop-student: $student
spec:
  request: >-
    Investigate the deliberately failed ParksMap readiness rollout in
    namespace $target_namespace. The new deployment/parksmap Pod is
    Running but Not Ready after a GitOps update; the old healthy Pod
    may still serve traffic because RollingUpdate preserves availability.
    Deployment/nationalparks and Deployment/mongodb-nationalparks
    should remain healthy. Inspect Kubernetes Deployment and Pod status,
    readinessProbe configuration, old/new ReplicaSets, Pod events,
    Service endpoints, Routes,
    logs and the GitOps Application national-parks-settings in
    namespace $student-demo when permitted. Distinguish confirmed
    facts from guesses and propose the smallest source-controlled
    correction in the student Gitea main branch. Do not modify,
    patch, create, delete or scale any workload. Do not read Secrets.
  analysis:
    agent: default
YAML

echo
echo "Created analysis-only run: $operator_namespace/$run_name"
echo "No execution or verification stage was configured."
echo "Review through the Agentic Runs UI or:"
echo "  oc get agenticrun $run_name -n $operator_namespace -o yaml"
echo "Do NOT approve execution; repair the application via student Gitea."
