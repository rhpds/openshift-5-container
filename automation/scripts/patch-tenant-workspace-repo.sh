#!/usr/bin/env bash
# Point an existing student tenant bootstrap at the flat workspace repository.
# Read-only unless --apply is given.
set -euo pipefail

WORKSPACE_NAME="openshift-5-container-workspace"
WORKSPACE_URL="https://github.com/rhpds/${WORKSPACE_NAME}"

usage() {
  cat <<'HELP'
Usage: bash automation/scripts/patch-tenant-workspace-repo.sh -n user-<guid>-demo [--apply]

Rewrite the Argo CD tenant Application helm values so Gitea imports only the
flat workspace repository. Existing credentials and deployer values are kept.

Without --apply it prints the Application name and the new values.

After applying, reconcile the tenant so Gitea imports the new repository:
  bash automation/scripts/reconcile-gitea-repositories.sh -n user-<guid>-demo --apply
HELP
}

NS=""
APPLY=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    -n) NS="${2:-}"; shift 2 ;;
    --apply) APPLY=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -n "$NS" ]] || { usage >&2; exit 2; }
STUDENT="${NS%-demo}"
[[ "$STUDENT" != "$NS" ]] || { echo "Expected a -demo namespace, got $NS" >&2; exit 2; }

for tool in oc jq python3; do
  command -v "$tool" >/dev/null || { echo "Missing $tool" >&2; exit 2; }
done

APP="$(oc get applications -n openshift-gitops -o json | jq -r --arg u "username: $STUDENT" '
  .items[]
  | select(.spec.source.path == "automation/gitops/bootstrap-tenant")
  | select((.spec.source.helm.values // "") | contains($u))
  | .metadata.name' | head -1)"

[[ -n "$APP" ]] || { echo "No tenant bootstrap Application found for $STUDENT" >&2; exit 1; }

NEW_VALUES="$(oc get application "$APP" -n openshift-gitops -o json \
  | jq -r '.spec.source.helm.values' \
  | python3 -c '
import sys, yaml
values = yaml.safe_load(sys.stdin) or {}
values.setdefault("gitea", {})["migrateRepos"] = [{
    "name": "'"$WORKSPACE_NAME"'",
    "url": "'"$WORKSPACE_URL"'",
    "private": False,
}]
print(yaml.safe_dump(values, sort_keys=False), end="")
')"

echo "Application: openshift-gitops/$APP"
echo "--- new helm values (credentials redacted) ---"
printf '%s\n' "$NEW_VALUES" | sed -E 's/^( *)(adminPassword|password): .*/\1\2: [REDACTED]/'

if [[ "$APPLY" != true ]]; then
  echo "--- dry run; rerun with --apply to patch ---"
  exit 0
fi

oc patch application "$APP" -n openshift-gitops --type=merge \
  -p "$(jq -n --arg v "$NEW_VALUES" '{spec:{source:{helm:{values:$v}}}}')" >/dev/null
echo "Patched $APP. Wait for Argo CD to sync the Gitea CR, then run:"
echo "  bash automation/scripts/reconcile-gitea-repositories.sh -n $NS --apply"
