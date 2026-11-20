#!/usr/bin/env bash
# Render/reconcile a *dashboard only* for a preflighted student namespace.
# Usage:
#   bash automation/observability/prepare-student-perses-dashboard.sh user-lr9lj
#   bash automation/observability/prepare-student-perses-dashboard.sh user-lr9lj --apply --tenant-query-isolation-verified
#
# Does not install COO, create metrics credentials, copy the built-in Thanos
# Secret or grant cross-tenant monitoring access. Run as instructor/admin.
set -euo pipefail

usage() {
  printf 'Usage: bash %s user-<guid> [--apply --tenant-query-isolation-verified]\n' "$0"
}
if (( $# < 1 )); then usage; exit 2; fi

student="$1"; shift
if [[ ! "$student" =~ ^user-[a-z0-9]{4,12}$ ]]; then
  printf 'ERROR: expected student identity user-<guid>, got %q\n' "$student" >&2
  exit 2
fi
apply=false
confirmed=false
for arg in "$@"; do
  case "$arg" in
    --apply) apply=true ;;
    --tenant-query-isolation-verified) confirmed=true ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'ERROR: unknown argument: %s\n' "$arg" >&2; exit 2 ;;
  esac
done
if [[ "$apply" == true && "$confirmed" != true ]]; then
  printf 'ERROR: refusing to apply without --tenant-query-isolation-verified.\n' >&2
  exit 1
fi
namespace="${student}-gitops"
dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
template="$dir/workshop-workloads-dashboard.yaml"

for tool in oc sed mktemp; do
  command -v "$tool" >/dev/null || { echo "ERROR: required command $tool missing" >&2; exit 1; }
done
[[ -r "$template" ]] || { echo "ERROR: missing template $template" >&2; exit 1; }
oc get namespace "$namespace" >/dev/null || { echo "ERROR: namespace missing: $namespace" >&2; exit 1; }
oc get uiplugin monitoring >/dev/null || { echo "ERROR: UIPlugin/monitoring missing" >&2; exit 1; }
oc get persesdatasource workshop-workloads -n "$namespace" >/dev/null || {
  echo "ERROR: PersesDatasource/workshop-workloads not found in $namespace." >&2
  echo "Instructors must configure a *backend-enforced* tenant-scoped metrics proxy first." >&2
  echo "The operator-managed accelerators datasource is NOT an appropriate shortcut." >&2
  exit 1
}
tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT
sed "s/__NAMESPACE__/$namespace/g" "$template" > "$tmp"
echo "Student namespace: $namespace"
echo "Datasource: PersesDatasource/workshop-workloads (existence only; isolation independently preflighted)"
if [[ "$apply" == true ]]; then
  echo "APPLY: instructor has attested independent tenant query isolation"
  oc apply -n "$namespace" -f "$tmp"
  oc get persesdashboard workshop-workloads -n "$namespace"
else
  echo "DRY RUN: showing prospective manifest; no resources changed."
  cat "$tmp"
  echo
  echo "After independent tenant-query isolation validation, rerun with:"
  echo "  bash $0 $student --apply --tenant-query-isolation-verified"
fi
