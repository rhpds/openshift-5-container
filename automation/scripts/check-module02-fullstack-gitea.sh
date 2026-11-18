#!/usr/bin/env bash
# Read-only preflight: reject stale or incomplete student Gitea workspaces.
# Does not push, sync or change any GitOps or Kubernetes resources.
set -euo pipefail

usage() {
  cat <<'HELP'
Usage: bash automation/scripts/check-module02-fullstack-gitea.sh GITEA_REPO_URL [GITEA_REPO_URL...]

Check every public student Gitea main branch before Module 2.
The workspace root must deploy the entire National Parks stack through a
single root kustomization.yaml. Any failed repository makes the command exit 1.

Example:
  bash automation/scripts/check-module02-fullstack-gitea.sh \
    https://gitea-user-xtm9x-demo.apps.example.com/user-xtm9x/openshift-5-container-workspace.git

This command is read-only. It cannot repair failed Gitea pushes (AUTH_FAILED).
HELP
}

if (( $# == 0 )) || [[ "${1:-}" == "--help" ]]; then
  usage
  if (( $# == 0 )); then exit 2; else exit 0; fi
fi

for command in git awk grep mktemp; do
  if ! command -v "$command" >/dev/null 2>&1; then
    printf 'Missing required command: %s\n' "$command" >&2
    exit 2
  fi
done

scratch="$(mktemp -d)"
trap 'rm -rf "$scratch"' EXIT

required=(
  national-parks-gitops-info.yaml
  00-mongodb-credentials.yaml
  01-mongodb.yaml
  02-nationalparks-backend.yaml
  03-parksmap-discovery.yaml
  04-parksmap-frontend.yaml
  05-park-data-bootstrap.yaml
)

# The root Kustomization must reference every National Parks manifest exactly
# once. This is the difference between the flat workspace and the previous
# ConfigMap-only exercise.
root_lists_required() {
  local manifest
  for manifest in "${required[@]}"; do
    awk -v expected="$manifest" '
      /^resources:[[:space:]]*$/ { in_resources = 1; next }
      in_resources && /^[^[:space:]#]/ { in_resources = 0 }
      in_resources && /^[[:space:]]*-[[:space:]]*/ {
        item = $0
        sub(/^[[:space:]]*-[[:space:]]*/, "", item)
        sub(/[[:space:]]*(#.*)?$/, "", item)
        if (item == expected) found = 1
      }
      END { exit !found }
    ' "$1" || return 1
  done
  return 0
}

failed=0
number=0
for repo_url in "$@"; do
  number=$((number + 1))
  checkout="$scratch/$number"

  # Only public HTTPS clone URLs without embedded credentials are supported.
  if [[ ! "$repo_url" =~ ^https://[^/@]+/[^/]+/openshift-5-container-workspace(\.git)?/?$ ]]; then
    printf 'FAIL %s: expected a public HTTPS openshift-5-container-workspace clone URL with no credentials.\n' "$repo_url" >&2
    failed=1
    continue
  fi

  if ! GIT_TERMINAL_PROMPT=0 git -c credential.helper= -c core.askPass=/bin/false \
      clone --quiet --depth 1 --single-branch --branch main -- \
      "$repo_url" "$checkout" >/dev/null 2>&1; then
    printf 'FAIL %s: cannot clone main anonymously; check Gitea route, visibility and repository existence.\n' "$repo_url" >&2
    failed=1
    continue
  fi

  source_dir="$checkout/national-parks"
  root="$source_dir/kustomization.yaml"

  if [[ ! -f "$root" ]] || ! root_lists_required "$root"; then
    printf 'FAIL %s: national-parks/kustomization.yaml is missing or does not list all seven manifests.\n' "$repo_url" >&2
    failed=1
    continue
  fi

  missing=0
  for manifest in "${required[@]}"; do
    if [[ ! -s "$source_dir/$manifest" ]]; then
      printf 'FAIL %s: %s missing or empty.\n' "$repo_url" "$manifest" >&2
      missing=1
    fi
  done
  if (( missing != 0 )); then
    failed=1
    continue
  fi

  # Prevent an unexpected extra manifest from silently changing the exercise.
  resource_count="$(grep -Ec '^[[:space:]]*-[[:space:]]+[^[:space:]#]+\.yaml([[:space:]]*(#.*)?)?$' "$root" || true)"
  if [[ "$resource_count" -ne "${#required[@]}" ]]; then
    printf 'FAIL %s: expected exactly 7 National Parks resources; found %s.\n' "$repo_url" "$resource_count" >&2
    failed=1
    continue
  fi

  printf 'PASS %s: flat root Kustomization with 7 manifests on main.\n' "$repo_url"
done

if (( failed != 0 )); then
  printf 'BLOCKED: One or more student Gitea repositories are not ready for Module 2.\n' >&2
  exit 1
fi

printf 'READY: All supplied Gitea repositories contain the required National Parks stack.\n'
