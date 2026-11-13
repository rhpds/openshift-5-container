#!/usr/bin/env bash
# Safely backfill missing PUBLIC repositories in an existing student Gitea.
set -euo pipefail
usage() {
  cat <<'HELP'
Usage: bash automation/scripts/reconcile-gitea-repositories.sh -n NAMESPACE [--apply]
Without --apply: read-only comparison of desired public repositories with Gitea.
With --apply: reset migration status, toggle spec to trigger operator reconciliation,
and verify the expected repositories. No resources are deleted.
Supports one generated user and public repositories only.
HELP
}
NS=""
APPLY=0
while (( $# > 0 )); do
  case "$1" in
    -n|--namespace) if (( $# < 2 )); then usage >&2; exit 2; fi; NS="$2"; shift 2 ;;
    --apply) APPLY=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'Unknown argument: %s\n' "$1" >&2; usage >&2; exit 2 ;;
  esac
done
if [[ -z "$NS" || ! "$NS" =~ ^[a-z0-9]([-a-z0-9]*[a-z0-9])?$ ]]; then
  printf 'Specify a valid student namespace with -n.\n' >&2
  exit 2
fi
for tool in oc jq curl; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    printf 'Missing required command: %s\n' "$tool" >&2
    exit 2
  fi
done

CR="$(oc get gitea gitea -n "$NS" -o json)"
if ! printf '%s\n' "$CR" | jq -e '
  .spec.giteaCreateUsers == true
  and .spec.giteaMigrateRepositories == true
  and .spec.giteaUserNumber == 1
  and .status.userSetupComplete == true
  and ((.status.adminPassword // "") | length > 0)
  and (.spec.giteaRepositoriesList | type == "array" and length > 0)
' >/dev/null; then
  printf 'Gitea prerequisite check failed. Inspect the CR spec/status first.\n' >&2
  exit 1
fi

OWNER="$(printf '%s\n' "$CR" | jq -er '.spec.giteaGenerateUserFormat')"
GITEA_URL="$(printf '%s\n' "$CR" | jq -er '.status.giteaRoute')"
GITEA_URL="$(printf '%s' "$GITEA_URL" | sed 's:/$::')"
if [[ ! "$OWNER" =~ ^[a-zA-Z0-9._-]+$ || ! "$GITEA_URL" =~ ^https?:// ]]; then
  printf 'Invalid Gitea owner or Route URL.\n' >&2
  exit 1
fi
http_code() {
  curl --silent --show-error --connect-timeout 10 --max-time 30 \
    --output /dev/null --write-out '%{http_code}' \
    "$GITEA_URL/api/v1/repos/$OWNER/$1"
}

missing=()
missing_count=0
while IFS=$'\t' read -r name private; do
  if [[ ! "$name" =~ ^[a-zA-Z0-9._-]+$ ]]; then
    printf 'Invalid repository name: %s\n' "$name" >&2
    exit 1
  fi
  if [[ "$private" != "false" ]]; then
    printf 'Private repository requires authenticated verification: %s\n' "$name" >&2
    exit 1
  fi
  result="$(http_code "$name")"
  case "$result" in
    200) printf 'PRESENT %s/%s\n' "$OWNER" "$name" ;;
    404) missing+=("$name"); missing_count=$((missing_count + 1)); printf 'MISSING %s/%s\n' "$OWNER" "$name" ;;
    *) printf 'Unexpected Gitea HTTP %s for %s; stopping.\n' "$result" "$name" >&2; exit 1 ;;
  esac
done < <(printf '%s\n' "$CR" | jq -r '.spec.giteaRepositoriesList[] | [.name, (.private // false)] | @tsv')

if (( missing_count == 0 )); then
  printf 'All configured public repositories are present; no changes made.\n'
  exit 0
fi
if (( APPLY == 0 )); then
  printf 'DRY RUN: %d repository/repositories missing. Re-run with --apply.\n' "$missing_count"
  exit 0
fi

printf 'Triggering repository backfill for %s.\n' "$NS"
# The operator uses a one-time migration completion flag. A status-only patch
# did not trigger reconciliation reliably; change spec generation too.
oc patch gitea gitea -n "$NS" --subresource=status --type=merge \
  -p '{"status":{"repoMigrationComplete":false}}'
oc patch gitea gitea -n "$NS" --type=merge \
  -p '{"spec":{"giteaMigrateRepositories":false}}'
oc patch gitea gitea -n "$NS" --type=merge \
  -p '{"spec":{"giteaMigrateRepositories":true}}'

for attempt in $(seq 1 60); do
  ready=1
  for name in "${missing[@]}"; do
    result="$(http_code "$name")"
    if [[ "$result" != "200" ]]; then ready=0; fi
  done
  completed="$(oc get gitea gitea -n "$NS" -o json | jq -r '.status.repoMigrationComplete // false')"
  if (( ready == 1 )) && [[ "$completed" == "true" ]]; then
    printf 'SUCCESS: Gitea repositories verified and migration complete.\n'
    exit 0
  fi
  sleep 3
done
printf 'Backfill not confirmed. Inspect Gitea Operator reconciliation logs in openshift-operators.\n' >&2
exit 1
