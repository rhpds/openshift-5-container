# Module 3 — Agentic National Parks Deployment Incident: Instructor Preflight

## Purpose and scope

Module 3 is a **40-minute, five-mission** lab based on the two healthy National Parks stacks from Modules 1–2:

- Original native console deployment: user-<guid>-demo
- Independent Argo CD/Gitea deployment: user-<guid>-gitops
- Argo CD Application: national-parks-settings in user-<guid>-demo

The student commits one bad ParksMap readiness-probe port to **their own Gitea main branch**, sees a new Running but not Ready Pod while the old ready Pod may continue serving, uses Lightspeed to analyze live evidence, watches an instructor-led **analysis-only AgenticRun**, then restores the probe via Git. The original application and MongoDB are untouched.

This adapts the [OCP 5 First Look Agentic Troubleshooting lab](https://rhpds.github.io/ocp5-first-look-lab/modules/module-01-agentic-troubleshooting.html) without copying its global alert adapter/ApprovalPolicy changes or requiring cluster-admin students. In particular, **no student clicks Execute Remediation**.

## Core required preflight — per student

Verify both stacks are working and student Gitea contains the Module 2 fixes:

~~~bash
STUDENT=user-xxxxx # replace with actual student ID
oc get deploy -n "$STUDENT-demo"
oc get deploy -n "$STUDENT-gitops"
oc get application national-parks-settings -n "$STUDENT-demo" -o json | \
  jq '{sync: .status.sync.status, health: .status.health.status,
       revision: .status.sync.revision}'
oc get pvc -n "$STUDENT-gitops"
oc get route national-parks-app -n "$STUDENT-gitops" --show-labels
oc get deploy parksmap -n "$STUDENT-gitops" -o json | \
  jq '{wave: .metadata.annotations["argocd.argoproj.io/sync-wave"],
       probe: .spec.template.spec.containers[0].readinessProbe,
       limits: .spec.template.spec.containers[0].resources.limits}'
oc describe clusterresourcequota "tenant-$STUDENT"
~~~

Expected: all three GitOps Deployments 1/1 Ready, PVC Bound, Application Synced/Healthy, API Route does **not** carry type=parksmap-backend, the Service **does**, and ParksMap's probe uses port **http**. The tenant shared quota must have room for a replacement Pod. Do not inject an incident against an unhealthy baseline.

The student Gitea repository's main branch must contain:
content/modules/ROOT/examples/module02-gitops/fullstack/04-parksmap-frontend.yaml.
Imported Gitea repositories are not mirrors. Merging upstream GitHub does not automatically update them.

## Agentic integration gate (instructor only)

Do not assume that OpenShift 5 plus Lightspeed MCP implies the Agentic Operator is installed. Validate each component:

~~~bash
oc get crd agenticruns.agentic.openshift.io
oc get agent default -n openshift-lightspeed
oc get pods -n openshift-lightspeed
oc get llmprovider -n openshift-lightspeed
oc get approvalpolicy cluster -n openshift-lightspeed -o yaml

oc auth can-i create agenticruns.agentic.openshift.io -n openshift-lightspeed
oc auth can-i get agenticruns.agentic.openshift.io -n openshift-lightspeed
oc get consoleplugins -o name | grep -i agentic || true

# Optional CLI plug-in:
oc agentic --help || true
~~~

Agentic console and alerts adapter may be disabled. Verify that Agent/default has a working LLM and that the analysis sandbox is authorized only for intended namespace evidence. The sample custom resource uses **agentic.openshift.io/v1alpha1**, spec.request, and spec.analysis.agent=default, as documented in [openshift/lightspeed-agentic-operator](https://github.com/openshift/lightspeed-agentic-operator/blob/main/config/samples/agentic_v1alpha1_agenticrun.yaml).

The created resource deliberately **omits spec.execution and spec.verification**. The AI could still call other tools allowed by its configured analysis tools; an instruction not to mutate is not a robust security control. Inspect configured MCP tool permissions before allowing the run in the workshop.

If any prerequisite fails, use Lightspeed Troubleshooting and CLI evidence; record AgenticRun as unavailable. Do not install operators, enable alerts, or grant students cluster-admin during class.

## Instructor action — Mission 4

1. Wait until a chosen student has pushed the deliberately bad Gitea commit and the *live* readiness port is **18080**.
2. From your own authorized terminal and a checkout of this workshop repository:

~~~bash
STUDENT=user-xxxxx # replace with actual student ID
bash automation/scripts/create-module03-agentic-run.sh "$STUDENT"
~~~

3. The script checks CRD, Agent/default, permissions, namespace and live fault, and then creates one named run in openshift-lightspeed. Repeating it for the same student shows the existing run instead.
4. Review only that run:

~~~bash
STUDENT=user-xxxxx # replace with actual student ID
RUN_NAME="parksmap-$STUDENT-readiness"
oc get agenticrun "$RUN_NAME" -n openshift-lightspeed -o yaml
oc agentic run list  # only if plug-in is installed
~~~

5. Display the Agentic Runs UI to students, filtering to the selected run. Show Analysis evidence, Proposed/Completed/Failed status and the absence of any Execution stage. Do **not** approve execution.
6. The student verifies the live probe, events and Service endpoints and then restores port **http** in student Gitea.
7. Recheck ParksMap, National Parks API and MongoDB readiness; original namespace stays healthy.

**Capacity:** one instructor demonstration at a time, not 30 simultaneous LLM investigations. Do not grant broad access to AgenticRun records containing other students' findings.

## Expected signals and evidence

| Signal | Before | During incident | After Git repair |
| --- | --- | --- | --- |
| Gitea readiness port | http | 18080 | http |
| Container port | 8080 | 8080 | 8080 |
| ParksMap rollout | Healthy | New Pod 0/1; old Pod may remain 1/1 | New revision rolled out |
| ParksMap Service | Ready endpoints | Old ready endpoints usually remain during RollingUpdate | Ready new Pod endpoints |
| GitOps Application | Synced/Healthy | May be Synced/Degraded | Synced/Healthy |
| MongoDB & Python API | 1/1 | 1/1 | 1/1 |
| Original namespace | Healthy | Healthy | Healthy |
| AgenticRun | None | Analyzing → Proposed/Completed/Failed | Analysis only |

This is a **readiness TCP port mismatch on the new ReplicaSet**, not an image pull, MongoDB, OOM, or Route-discovery issue. Default RollingUpdate normally preserves an old ready Pod and a working Route even while the new rollout fails; do not assert an outage based only on a bad commit. Verify the new Pod's events and a stuck rollout using oc rollout status. On a busy cluster, quotas may prevent the replacement Pod from being scheduled; distinguish that condition from the intentional fault using events. Do not raise tenant quotas.

## Recovery

If students leave the bad change after class, correct the port to **http** in their own Gitea source and commit. Argo CD Auto-Sync should pick up the new revision:

~~~bash
oc get application national-parks-settings -n "$STUDENT-demo" -o json | \
  jq '{sync: .status.sync.status, health: .status.health.status,
       revision: .status.sync.revision,
       phase: .status.operationState.phase,
       message: .status.operationState.message}'
oc get deploy,pods -n "$STUDENT-gitops"
oc get events -n "$STUDENT-gitops" --sort-by=.lastTimestamp | tail -20
~~~

An old failed Argo CD operation may require the instructor to terminate that stale operation in the GitOps console, refresh and allow Auto-Sync at the new Git revision. Never delete the PVC, Secret, namespace or Application.

## Release acceptance

- [ ] Instructor validated real Lightspeed Troubleshooting tool responses.
- [ ] AgenticRun installed and usable, or fallback clearly communicated.
- [ ] Instructor demo creates analysis-only run without execution.
- [ ] Student bad Git commit makes the new ParksMap Pod's probe port 18080 and the rollout remains incomplete; old Pods may still serve.
- [ ] Both existing healthy backend/database Deployments remain healthy.
- [ ] Repair commit restores port http and all GitOps Deployments recover.
- [ ] Shared tenant quota and both namespaces verified without new quota objects.
- [ ] No student got broad openshift-lightspeed or cluster-admin access.
- [ ] Module 3 fault repaired before Module 4's different backend incident.
