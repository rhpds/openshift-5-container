# Student-created AgenticRuns — required security gate (Modules 3–5)

**Default: disabled.** The tenant chart sets `agenticStudent.enabled: false` and `agenticStudent.sandboxIsolationVerified: false`. The student-facing guide still has a complete read-only Lightspeed and instructor-run fallback.

## Why Kubernetes Namespace RBAC alone is not sufficient

The [upstream Agentic Operator RBAC design](https://github.com/openshift/lightspeed-agentic-operator/blob/main/docs/rbac.md) creates a unique per-step ServiceAccount for each AgenticRun **in the operator's namespace**. The current controller discovers ClusterRoleBindings referencing the `lightspeed-agent` seed and adds the per-step account to those bindings. Stock setup documents a cluster-wide reader binding.

This can let a student-created AgenticRun access other tenants' namespaces through its sandbox even when the user may create/read only AgenticRuns in their own namespace. **Do not mistake namespace-scoped AgenticRun RBAC or a prompt asking for a single namespace for sandbox isolation.** Operator versions in October 2026 also removed `spec.targetNamespaces`; adding that field cannot fix the problem.

## Supported use now

- Deploy and deliberately break WeatherNow using student Gitea and GitOps in `user-<guid>-gitops`.
- Run Lightspeed Troubleshooting using the student's existing read permissions; verify the MCP identity actually respects tenant boundaries.
- Instructor creates an analysis-only demonstration from an authorized context with an audited tool set.
- Students can inspect their own analysis results **only if that has been independently reviewed**.
- Do **not** set `agenticStudent.enabled=true` on an unmodified operator with global reader ClusterRoleBindings.

## Controls needed to turn on student creation later

1. **Operator update or isolated deployment:** obtain an operator-supported way to bind the analysis sandbox's per-step ServiceAccount only to the requesting tenant's namespace (no broad reader ClusterRoleBinding). Confirm no other inherited credentials or MCP endpoints can reach other tenants.
2. **Verify live cross-tenant denial:** from instructor/admin context, identify actual `ls-analysis-*` ServiceAccounts created for runs in tenant A. Check `oc auth can-i` for gets/lists of Pods, Pod logs, Services, ConfigMaps, Secrets and other resources in tenant B, and mutation rights in both namespaces. Test attempts via actual MCP tools, not solely with a command-line RBAC impersonation.
3. **Admission controls:** install and validate `automation/agentic/student-agenticrun-admission.yaml` and label *only* approved `user-<guid>-gitops` namespaces with `workshop.redhat.com/agentic-self-service=enabled`. Confirm the policy denies execution/verification stages, targetCluster, custom tools, reanalysis and non-default agent selection.
4. **Student RBAC:** only after the above gate passes, set `agenticStudent.enabled=true` **and** `agenticStudent.sandboxIsolationVerified=true` in the privileged tenant Helm deployment. The Role grants create/get/list/watch AgenticRuns plus get/list/watch AnalysisResults in the student's own GitOps namespace, no approval privileges, no edits/deletes and no direct workload access.
5. **Load and capacity:** analysis sandboxes consume resources in `openshift-lightspeed`, not the tenant's quota. Set classroom-wide concurrency limits and verify LLM and sandbox quota before enabling thirty simultaneous student investigations.

## Admin audit (read-only)

```bash
oc whoami
bash automation/scripts/check-student-agentic-isolation.sh
oc get validatingadmissionpolicy workshop-analysis-only-agenticruns
oc get validatingadmissionpolicybinding workshop-analysis-only-agenticruns
oc get agenticolsconfig
oc get agents.agentic.openshift.io
oc get llmproviders.agentic.openshift.io
oc auth can-i create agenticruns.agentic.openshift.io -n user-xxxxx-gitops --as=user-xxxxx
oc auth can-i create agenticruns.agentic.openshift.io -n user-yyyyy-gitops --as=user-xxxxx
```

**Expected now:** the audit should identify the upstream seed's cluster-wide reader RBAC and refuse to declare isolation. Student `create` should remain **no**. A Helm boolean by itself is only an administrative signoff, not security enforcement.

When a future operator implementation supplies tested tenant-constrained analysis sandboxes, verify:
- Student A may create and list runs in A's project, but not B's.
- Student A's run cannot read resources from B or any cluster-scope Secret.
- Student A's attempts to specify `execution`, `verification`, `targetCluster`, custom tools, or an unapproved Agent are rejected by admission.
- The instructor retains the ability to monitor failures without giving students access to the global operator namespace.

References: [operator architecture](https://github.com/openshift/lightspeed-agentic-operator/blob/main/ARCHITECTURE.md), [operator RBAC](https://github.com/openshift/lightspeed-agentic-operator/blob/main/docs/rbac.md).
