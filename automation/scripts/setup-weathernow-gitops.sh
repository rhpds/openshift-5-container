#!/usr/bin/env bash
# Safe first-run WeatherNow GitOps bootstrap for the assigned lab user.
# NEVER overwrites an existing student Gitea WeatherNow manifest.
set -euo pipefail
log() { printf '[weathernow] %s\n' "$*"; }
die() { printf '[weathernow] ERROR: %s\n' "$*" >&2; exit 1; }
if [[ "$#" -ne 0 ]]; then
  echo "Usage: bash setup-weathernow-gitops.sh" >&2
  exit 2
fi
for tool in oc git curl mktemp; do
  command -v "$tool" >/dev/null || die "Missing $tool"
done
STUDENT="$(oc whoami)"
[[ "$STUDENT" =~ ^user-[a-z0-9-]+$ ]] || die "Login as your user-<guid>, not $STUDENT"
DEMO_NS="$STUDENT-demo"
GITOPS_NS="$STUDENT-gitops"
oc get namespace "$GITOPS_NS" -o name >/dev/null || die "Missing $GITOPS_NS; ask instructor to repair bootstrap."
[[ "$(oc auth can-i create applications.argoproj.io -n "$GITOPS_NS")" == yes ]] \
  || die "Need student Application editor RBAC in $GITOPS_NS."
if oc get application weathernow-lab -n "$DEMO_NS" -o name >/dev/null 2>&1; then
  die "Existing weathernow-lab in legacy -demo namespace. Ask instructor; do not create duplicate."
fi

GITEA_ROUTE="$(oc get gitea gitea -n "$DEMO_NS" -o jsonpath='{.status.giteaRoute}' 2>/dev/null || true)"
if [[ -z "$GITEA_ROUTE" ]]; then
  GITEA_ROUTE="$(oc get routes -n "$DEMO_NS" -o jsonpath='{range .items[*]}{.spec.host}{"\n"}{end}' | grep '^gitea-' | head -1 || true)"
fi
[[ -n "$GITEA_ROUTE" ]] || die "Unable to find student Gitea Route"
GITEA_ROUTE="$(printf '%s' "$GITEA_ROUTE" | sed 's|^https://||;s|^http://||;s|/$||')"
GITEA_REPO="https://$GITEA_ROUTE/$STUDENT/openshift-5-container.git"
SOURCE="content/modules/ROOT/examples/module04-weathernow"
# Override this root to test the feature branch before merging upstream.
WEATHERNOW_RAW_ROOT="${WEATHERNOW_RAW_ROOT:-https://raw.githubusercontent.com/rhpds/openshift-5-container/main}"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
log "Cloning student-owned Gitea main: $GITEA_REPO"
git -c credential.interactive=never clone --quiet --depth 1 --branch main "$GITEA_REPO" "$WORK/repo" \
  || die "Cannot clone student Gitea repo. Check credentials and that it exists."
mkdir -p "$WORK/repo/$SOURCE"
RAW_ROOT="$(printf '%s' "$WEATHERNOW_RAW_ROOT" | sed 's|/$||')"
BASE_URL="$RAW_ROOT/$SOURCE"
for file in kustomization.yaml weathernow.yaml; do
  if [[ -e "$WORK/repo/$SOURCE/$file" ]]; then
    log "Preserving existing $file, even if it is deliberately broken."
  else
    curl -fsSL "$BASE_URL/$file" -o "$WORK/repo/$SOURCE/$file" \
      || die "WeatherNow source unavailable upstream; ensure PR merged or ask instructor for file."
  fi
done
(
  cd "$WORK/repo"
  git add "$SOURCE/kustomization.yaml" "$SOURCE/weathernow.yaml"
  if ! git diff --cached --quiet; then
    git -c user.name="$STUDENT" -c user.email="$STUDENT@workshop.invalid" \
      commit -qm "lab(weather): add lightweight WeatherNow GitOps source"
    log "Pushing only new WeatherNow source files to student Gitea."
    git push origin main || die "Gitea push failed; use your student Gitea credentials/token."
  else
    log "Nothing to commit; existing source remains unchanged."
  fi
)
if oc get application weathernow-lab -n "$GITOPS_NS" -o name >/dev/null 2>&1; then
  CURRENT_URL="$(oc get application weathernow-lab -n "$GITOPS_NS" -o jsonpath='{.spec.source.repoURL}')"
  CURRENT_PATH="$(oc get application weathernow-lab -n "$GITOPS_NS" -o jsonpath='{.spec.source.path}')"
  [[ "$CURRENT_URL" == "$GITEA_REPO" && "$CURRENT_PATH" == "$SOURCE" ]] \
    || die "Existing weathernow-lab points to unexpected repo/path; refusing overwrite."
  log "Keeping existing GitOps Application."
else
  cat <<YAML | oc create -n "$GITOPS_NS" -f -
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: weathernow-lab
  namespace: $GITOPS_NS
spec:
  project: default
  source:
    repoURL: $GITEA_REPO
    targetRevision: main
    path: $SOURCE
  destination:
    server: https://kubernetes.default.svc
    namespace: $GITOPS_NS
  syncPolicy:
    automated:
      enabled: true
      prune: false
      selfHeal: true
    retry:
      limit: 5
      backoff:
        duration: 10s
        factor: 2
        maxDuration: 2m
YAML
fi
log "WeatherNow is managed separately from National Parks:"
log "  oc get application weathernow-lab -n $GITOPS_NS"
log "  oc get deployment,service,route weathernow -n $GITOPS_NS"
log "Do not rerun setup during a deliberate Module 4/5 incident."
