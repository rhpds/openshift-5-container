#!/usr/bin/env bash
# Instructor/admin diagnostic only; NO cluster changes.
# Fail closed when operator reader bindings may grant cross-tenant reads.
set -euo pipefail
note(){ printf '[agentic-security] %s\n' "$*"; }
die(){ printf '[agentic-security] BLOCKED: %s\n' "$*" >&2; exit 1; }
command -v oc >/dev/null || die "oc required"
command -v python3 >/dev/null || die "python3 required"
note "Logged in as $(oc whoami); requires instructor/admin read access."
oc get crd agenticruns.agentic.openshift.io -o name >/dev/null || die "AgenticRun CRD missing."
oc get agents.agentic.openshift.io -o name >/dev/null || die "Cannot read cluster-scoped Agents."
oc get llmproviders.agentic.openshift.io -o name >/dev/null || die "Cannot read cluster-scoped LLMProviders."
note "Checking reader ClusterRoleBindings based on lightspeed-agent seed."
# Any ClusterRoleBinding gives a cluster-wide RBAC scope. A controller that
# enrolls per-run sandboxes into these bindings is not namespace isolated.
oc get clusterrolebindings -o json | python3 -c '
import json,sys
bindings=json.load(sys.stdin).get("items",[])
rows=[]
for item in bindings:
    names=[s for s in item.get("subjects",[])
           if s.get("kind")=="ServiceAccount" and s.get("name")=="lightspeed-agent"]
    if names:
        rows.append((item["metadata"]["name"],item.get("roleRef",{}).get("name","")))
for name,role in rows:
    print("GLOBAL READER SEED BINDING:",name,"->",role)
if rows:
    sys.stderr.write("BLOCKED: per-step AgenticRun sandboxes can inherit cluster-wide reader bindings.\n")
    sys.exit(3)
print("No shared lightspeed-agent reader CRBs found. This is only a prerequisite, NOT proof of isolation.")
' || die "Global reader model or CRB read failure; DO NOT enable per-student AgenticRuns."
note "Now verify actual per-run ServiceAccount RBAC from tenant A to tenant B."
note "For each analysis SA, run: oc auth can-i list pods -n user-B-gitops --as=system:serviceaccount:openshift-lightspeed:SA_NAME"
note "Also test secrets, configmaps, pods/log, namespaces, and mutation against both tenants."
note "Confirm agent MCP tools and kubeconfig are tenant-bound and admission policy is installed."
note "Only documented manual security signoff may set agenticStudent.enabled=true."
