# Module 4 — WeatherNow Agentic Troubleshooting: Instructor Preflight

This 40-minute module uses a **separate lightweight WeatherNow workload** in each student's existing \`user-<guid>-gitops\` namespace, *not* the National Parks Python backend and MongoDB. WeatherNow runs \`quay.io/openshift-workshop-applications/weathernow:latest\` with port 8080 and 200m/128Mi resource limits.

## Before the students enter

1. Confirm the GitOps namespace already exists and \`Application/national-parks-settings\` is running there. No Namespace creation is part of this module.
2. Merge the WeatherNow manifest into the upstream workshop repository, then make it available to each student Gitea repo using the \`setup-weathernow-gitops.sh\` helper. The helper creates a *second* Argo CD Application \`weathernow-lab\` in \`user-<guid>-gitops\`, targeting \`content/modules/ROOT/examples/module04-weathernow\`. This preserves all National Parks manifests.
3. Verify the student's Application editor RBAC and namespace quota. A student should be able to create an Application in their own \`-gitops\` namespace, not in another student's.
4. Rehearse at least one WeatherNow image pull, Route creation, and application readiness check under the real cluster:
   
   \`\`\`bash
   STUDENT=user-xxxxx
   NS="$STUDENT-gitops"
   oc get application weathernow-lab -n "$NS"
   oc get deployment,service,route weathernow -n "$NS"
   oc rollout status deployment/weathernow -n "$NS" --timeout=120s
   HOST="$(oc get route weathernow -n "$NS" -o jsonpath='{.spec.host}')"
   curl -sS -o /dev/null -w '%{http_code}\n' "https://$HOST/"
   \`\`\`

## Incident

The student edits **only** \`content/modules/ROOT/examples/module04-weathernow/weathernow.yaml\` in their Gitea main branch, replacing the readiness port \`http\` with \`18080\`. Do not touch the liveness port or Service. Argo CD Auto-Sync applies the change; a new Pod should fail readiness while the old Pod can continue to serve its Route.

Lightspeed diagnosis compares Deployment probe, actual 8080 container port, old/new ReplicaSets, Pod events and GitOps source. The repair is a Gitea commit restoring \`port: http\`, not a live \`oc patch\`.

## AgenticRun security — required gate

**Student AgenticRuns are disabled by default.** Consult \`docs/instructor/agentic-student-isolation-gate.md\` before granting *any* student access. The current upstream operator may add per-run analysis ServiceAccounts to *cluster-wide reader ClusterRoleBindings*; a namespaced Role on AgenticRun is not a safe per-student sandbox boundary.

- Run \`bash automation/scripts/check-student-agentic-isolation.sh\` from authorized instructor/admin context; with stock global reader RBAC it should fail closed.
- Only after an operator-supported, verified per-tenant sandbox isolation feature is available, install the cluster-admin \`automation/agentic/student-agenticrun-admission.yaml\`, test its denials and set the tenant chart opt-in values. Until then, **do not enable** \`agenticStudent.enabled\`.
- Student guide creates an analysis-only CR in their own \`-gitops\` namespace *only if* they have create permission. Otherwise use Lightspeed and an instructor-led demo. Never approve execution or expose student Secrets.
- Stage runs to avoid LLM/sandbox load spikes across 30 students.

## Acceptance checklist

- [ ] WeatherNow is 1/1 Ready before the incident; the existing two National Parks stacks remain healthy.
- [ ] The new bad-readiness Pod is 0/1, and its events show port 18080 refusal or timeout.
- [ ] The old ready Pod may remain active: do not falsely report an outage if the Route stays HTTP 200.
- [ ] Lightspeed/CLI evidence identifies the specific configuration defect.
- [ ] Student AgenticRun creation is **no** unless sandbox isolation admission tests have passed, otherwise instructor demo.
- [ ] Repair Gitea commit restores port \`http\`; \`weathernow-lab\` returns Synced/Healthy, and new Pod is 1/1.
- [ ] No Secrets, database, PVC, quota or other student namespaces touched.
