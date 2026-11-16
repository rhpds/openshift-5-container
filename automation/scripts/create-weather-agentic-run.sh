#!/usr/bin/env bash
# Instructor-only: create an advisory AgenticRun for a known WeatherNow fault.
# This does not change any workload or approve remediation.
set -euo pipefail
usage(){ printf 'Usage: bash create-weather-agentic-run.sh 4|5 user-<guid>\n' >&2; exit 2; }
[[ "$#" -eq 2 ]] || usage
MODULE="$1"
STUDENT="$2"
[[ "$MODULE" == 4 || "$MODULE" == 5 ]] || usage
[[ "$STUDENT" =~ ^user-[a-z0-9-]+$ ]] || usage
NS="$STUDENT-gitops"
OP_NS=openshift-lightspeed
command -v oc >/dev/null || { echo "oc required" >&2; exit 1; }
oc get namespace "$NS" -o name >/dev/null || exit 1
oc get crd agenticruns.agentic.openshift.io -o name >/dev/null || exit 1
[[ "$(oc auth can-i create agenticruns.agentic.openshift.io -n "$OP_NS")" == yes ]] \
  || { echo "Instructor not authorized to create AgenticRuns" >&2; exit 1; }
oc get agent default -o name >/dev/null || { echo "Agent/default unavailable" >&2; exit 1; }

if [[ "$MODULE" == 4 ]]; then
  EXPECTED="$(oc get deployment weathernow -n "$NS" -o jsonpath='{.spec.template.spec.containers[0].readinessProbe.tcpSocket.port}')"
  [[ "$EXPECTED" == 18080 ]] || { echo "No deliberate Module 4 fault in $NS" >&2; exit 1; }
  NAME="weather-$STUDENT-readiness"
  REQUEST="Analyze WeatherNow's failed TCP readiness probe in namespace $NS only. The new Pod uses 18080, but the server listens on 8080. Inspect Pod/ReplicaSet/events as permitted. Explain why the old Pod can still serve traffic and recommend the smallest Git correction. Do not read Secrets, inspect other namespaces or modify resources."
else
  EXPECTED="$(oc get deployment weathernow -n "$NS" -o jsonpath='{.spec.template.spec.containers[0].image}')"
  [[ "$EXPECTED" == quay.io/openshift-workshop-applications/weathernow:module05-intentional-bad-tag ]] \
    || { echo "No deliberate Module 5 bad-image fault in $NS" >&2; exit 1; }
  NAME="weather-$STUDENT-image"
  REQUEST="Analyze why the new WeatherNow image cannot be pulled in namespace $NS only. Check the current bad tag, Pod events and ReplicaSets. Recommend restoring the latest image tag through student Gitea. Do not read Secrets, inspect other namespaces or modify resources."
fi

if oc get agenticrun "$NAME" -n "$OP_NS" -o name >/dev/null 2>&1; then
  echo "Existing run: $OP_NS/$NAME; review rather than creating a duplicate."
  exit 0
fi

cat <<YAML | oc create -n "$OP_NS" -f -
apiVersion: agentic.openshift.io/v1alpha1
kind: AgenticRun
metadata:
  name: $NAME
  namespace: $OP_NS
  labels:
    app.kubernetes.io/part-of: weathernow-lab
    workshop-student: $STUDENT
spec:
  request: >-
    $REQUEST
  analysis:
    agent: default
YAML
echo "Analysis-only instructor demonstration: $OP_NS/$NAME"
echo "Never approve execution or change the student's Git source from this script."
