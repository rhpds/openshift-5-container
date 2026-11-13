# Module 2 preflight — Full National Parks GitOps Auto-Sync

This is the **main Module 2 workshop**, not an extension. Students use the
GA OpenShift GitOps console plug-in to deploy a **complete, independent**
ParksMap + Python API + MongoDB 8 stack into user-<guid>-gitops with
automatic reconciliation. Module 1 continues in user-<guid>-demo.

**Duration:** 45 minutes after cluster and Gitea preflight. Do not count
instructor repairs against student time.

## 1. Ensure ALL student Gitea repositories have the latest source

Student Gitea repositories are editable imported copies, **not live
GitHub mirrors**. Even after an upstream merge, each copy must receive
the update before students enter Module 2.

Required Gitea main branch structure:

~~~text
content/modules/ROOT/examples/module02-gitops/
  kustomization.yaml                    # resources: - fullstack
  fullstack/
    kustomization.yaml
    national-parks-gitops-info.yaml
    00-mongodb-credentials.yaml
    01-mongodb.yaml
    02-nationalparks-backend.yaml
    03-parksmap-discovery.yaml
    04-parksmap-frontend.yaml
    05-park-data-bootstrap.yaml
~~~

Check every student's root kustomization.yaml: it MUST contain
"resources: - fullstack" rather than only national-parks-gitops-info.yaml.
The lesson does not require students to migrate, reimport, or create
repositories themselves.

**Live environment blocker (13 Nov 2026):** an earlier ten-student bulk
sync job discovered all ten Gitea routes and validated ten clean merges,
but **every authenticated push failed** (AUTH_FAILED). That does **not**
mean student repositories are up to date. Fix Git write authentication,
perform a single-student pilot, and verify all ten Gitea main branches.
Use preview and conflict-preserving merges; never force-push or put
passwords/tokens in logs.

### Mandatory release gate: audit each imported Gitea main branch

After repairing write authentication and synchronizing student repositories,
run the **read-only** full-stack checker against *all ten* public Gitea clone
URLs. This confirms that the root Kustomization selects `fullstack` and
that all seven required manifests are present and referenced:

~~~bash
bash automation/scripts/check-module02-fullstack-gitea.sh \
  https://gitea-user-xtm9x-demo.apps.example.com/user-xtm9x/openshift-5-container.git \
  https://gitea-user-another-demo.apps.example.com/user-another/openshift-5-container.git
# Supply the real clone URL for EVERY student; the two above are examples.
~~~

The script never pushes, reads credentials, patches Kubernetes, or fixes
`AUTH_FAILED`. A failing or missing repository **blocks Module 2**.
Do not bypass this by pointing Argo CD directly at upstream GitHub:
students must be able to commit to their own Gitea clone in Mission 5.

**A green Argo CD badge is not this release gate.** An Application can be
Healthy/Synced with only the legacy `national-parks-gitops-info` ConfigMap.
Inspect the resource tree and verify the three Deployments exist in the
destination namespace before declaring a student environment ready.

## 2. Confirm Namespace, quota, RBAC and Argo CD controller access

The privileged tenant GitOps bootstrap declaratively provisions
user-<guid>-gitops. It adds:

* argocd.argoproj.io/managed-by: user-<guid>-demo
* openshift.io/requester: user-<guid>
* RoleBinding/module02-student-view in -gitops

The same student ClusterResourceQuota covers both student namespaces.
**Do not add Namespace YAML to student GitOps or grant students
cluster-wide Namespace/Secret rights.** The student Application CR remains
in -demo, but destinations target -gitops.

~~~bash
USER_NAME=user-xtm9x
ARGO_NS="$USER_NAME-demo"
APP_NS="$USER_NAME-gitops"

oc get namespace "$APP_NS" \
  -o jsonpath='{.metadata.labels.argocd\.argoproj\.io/managed-by}{" / "}{.metadata.annotations.openshift\.io/requester}{"\n"}'
oc get rolebinding module02-student-view -n "$APP_NS"
oc get clusterresourcequota "tenant-$USER_NAME"
oc get argocd argocd -n "$ARGO_NS"
oc auth can-i create applications.argoproj.io -n "$ARGO_NS" --as="$USER_NAME"
oc auth can-i get configmaps -n "$APP_NS" --as="$USER_NAME"
oc auth can-i get deployments.apps -n "$APP_NS" --as="$USER_NAME"
~~~

Expected managed-by user-xtm9x-demo, requester user-xtm9x, and
namespace-visible resources. **Also** validate the actual Argo CD
application-controller ServiceAccount can create/update all types
managed in -gitops: Deployments, Services, Routes, BuildConfigs,
ImageStreams, ConfigMaps, PVCs, ServiceAccounts, Roles, RoleBindings
and Jobs. The namespace management label requires GitOps Operator
reconciliation. Don't assume students can patch -gitops because they
can view it. Default AppProject may be permissive; scope the lab
through the reviewed Kustomization source, not a false claim of
ConfigMap-only AppProject policies.

### CPU and memory: combined two-namespace quota

The ClusterResourceQuota named `tenant-<user>` applies to **both**
`user-<guid>-demo` and `user-<guid>-gitops` via the
`openshift.io/requester` annotation. The configured hard limits are
4 CPU requests / 8 CPU limits, 8Gi memory requests / 12Gi memory limits,
and 20Gi storage requests across both namespaces.

Every Deployment container, BuildConfig build Pod and Job container
**must set requests.cpu, limits.cpu, requests.memory and limits.memory**.
Otherwise the Pod is rejected with
`failed quota: tenant-<user>: must specify limits.cpu` even when quota
capacity is available.

A snapshot from one test tenant (`user-p2z9v`, 13 November 2026)
showed 1650m/4 CPU requests, 3500m/8 CPU limits,
2816Mi/8Gi memory requests, 5Gi/12Gi memory limits,
and 2Gi/20Gi storage requests already used across both projects.
With the corrected full-stack defaults, even **conservatively** counting
the three Deployments, Docker build and both Jobs at once, Module 2 adds
525m CPU requests, 3150m CPU limits, 1312Mi memory requests,
4800Mi memory limits and 1Gi PVC storage. The estimated peaks would
be 2175m/4 CPU requests, 6650m/8 CPU limits,
4128Mi/8Gi memory requests, 9920Mi/12Gi memory limits
and 3Gi/20Gi storage requests. The build and Jobs do not normally all
overlap, so this deliberately overestimates simultaneous usage.

This illustrates that two National Parks stacks **can fit the reported
quota**, not that the same spare capacity is guaranteed for every
student. Check `oc describe clusterresourcequota tenant-<user>`
immediately before every rehearsal; leave headroom for rollouts,
other tenant workloads and image builds. Never raise the shared
quota merely to cure an omitted `limits.cpu` field.

### Recover a failed credentials bootstrap Job after updating Gitea

The original `nationalparks-credentials-bootstrap` may have reached
`DeadlineExceeded` because admission rejected every Pod due to its
missing CPU limit. Updating YAML alone cannot patch the immutable
Job Pod template. Once the **corrected files are committed to that
student's Gitea `main` branch** (upstream GitHub alone is insufficient),
an instructor/admin may remove **only the failed Job**:

~~~bash
oc get job nationalparks-credentials-bootstrap -n user-p2z9v-gitops
oc delete job nationalparks-credentials-bootstrap -n user-p2z9v-gitops
# Then refresh the existing Argo CD Application and inspect Auto-Sync:
oc get applications.argoproj.io national-parks-settings -n user-p2z9v-demo
oc get jobs,pods -n user-p2z9v-gitops
~~~

Run the deletion **only when the Job is Failed** and the revised GitOps
source is available. Do **not** delete the MongoDB Secret or PVC;
the credentials Job is designed to preserve an existing Secret.
Auto-Sync/Self-Heal should reconcile a missing Git-managed Job;
if it does not, inspect the Application's sync history and controller
events rather than repeatedly deleting workloads.

## 3. Confirm GitOps 1.22 console plug-in and default Auto-Sync

The student workflow **requires** OCP Console -> GitOps -> Applications.
Enable the GA plug-in before class and verify a real student can create
an Application in -demo and see its Details, Sources and Resources.

~~~bash
oc get consoleplugins.console.openshift.io gitops-plugin
oc get consoles.operator.openshift.io cluster -o jsonpath='{.spec.plugins}{"\n"}'
~~~

The Application example is at
content/modules/ROOT/examples/module02-gitops/fullstack-application-example.yaml
and the student guide includes a per-user YAML with:

* spec.source.path: content/modules/ROOT/examples/module02-gitops
* spec.destination.namespace: user-<guid>-gitops
* spec.syncPolicy.automated.enabled: true
* selfHeal: true; prune: false
* narrow ignoreDifferences on Deployment/nationalparks image field
* RespectIgnoreDifferences=true

**No manual Sync in the student flow.** Auto-Sync is the objective.
The image difference exception allows OpenShift's ImageStreamTag
image trigger to update the Python backend Deployment without
Argo CD self-heal fighting the image digest. Do not ignore other
Deployment fields or weaken tenant RBAC.

## 4. Rehearse all workloads and dependencies before class

The root Kustomization must deploy the complete fullstack/ directory,
including:

* Three Deployments, Services: parksmap, nationalparks, mongodb-nationalparks.
* Two HTTPS Routes: parksmap and national-parks-app.
* Python BuildConfig + ImageStream producing nationalparks:latest.
* MongoDB 8 with a 1Gi PVC and the CORRECT Service port 27017.
* Namespaced Secret-generation Job and least-privilege RBAC (no plaintext
  database passwords committed to Git).
* Dedicated read-only ParksMap backend discovery identity.
* A PostSync Job that loads sample park data only if collection is empty.
* The Git-managed informational ConfigMap.

Perform **two complete end-to-end rehearsals using real disposable student
identities**. Verify all of the following in the actual workshop cluster:

* Image pulls for ParksMap, MongoDB, openshift4/ose-cli and curlimages/curl.
* Default StorageClass binds the MongoDB PVC.
* Quota has sufficient memory/CPU for three extra Deployments and a build.
* Dockerfile BuildConfig can reach its GitHub source and publish an
  ImageStreamTag to the OpenShift internal registry.
* Credentials bootstrap Job can create the namespaced Secret; never print
  passwords or tokens in logs or screenshots.
* Deployment/nationalparks receives the built image through its trigger.
* The two Routes are admitted with HTTPS and discover each other through
  the proper Services/Routes labels and ParksMap discovery RBAC.
* Python API /ws/data/all returns a NONEMPTY list; /ws/healthz/ alone is
  not evidence of MongoDB health.
* The original three Module 1 Deployments are still ready in -demo.

~~~bash
oc get application national-parks-settings -n "$ARGO_NS" \
  -o jsonpath='{.spec.source.path}{"\n"}{.spec.destination.namespace}{"\n"}{.spec.syncPolicy.automated}{"\n"}'
oc get jobs,pvc,buildconfigs,imagestreams -n "$APP_NS"
oc get deployments,services,routes -n "$APP_NS"
oc get secret nationalparks-mongodb-parameters -n "$APP_NS" -o name
oc get svc mongodb-nationalparks -n "$APP_NS" \
  -o jsonpath='{.spec.ports[0].port}{" -> "}{.spec.ports[0].targetPort}{"\n"}'
oc get route national-parks-app -n "$APP_NS" \
  -o jsonpath='{.spec.host}{"\n"}'
~~~

The credentials-bootstrap Job is a normal managed Job. The park-data
loader is a PostSync Hook with HookSucceeded deletion; its Job may
disappear after completing. Review sync operation history rather than
assuming a missing completed Hook is an error. The /ws/data/load endpoint
deletes and reloads the collection: **do not repeatedly invoke it** or
use production data.

## 5. Verify one Gitea commit triggers automatic reconciliation

As a student, edit ONLY
content/modules/ROOT/examples/module02-gitops/fullstack/national-parks-gitops-info.yaml
in the assigned Gitea repository. Commit a message change to
"Updated through GitOps Auto-Sync" on main.

Verify the actual GitOps Application automatically updates the live
ConfigMap in -gitops **without a manual Sync**. Reconciliation may
happen quickly enough that OutOfSync is never visible. Check Gitea,
the GitOps console and an oc get ConfigMap read, not only AI output.

Students usually have view permission in -gitops. Do not instruct
them to patch a Deployment to test Self-Heal. Explain the policy
without bypassing student Kubernetes permissions.

Check the student RBAC boundary against openshift-config and ensure
Module 1 workloads remain unchanged.

## 6. Screenshot and next-module release gate

Replace the 12 existing SVG placeholders with genuine captures of the
**new full-stack Auto-Sync** experience. The old single-ConfigMap,
manual-sync screenshots do not qualify.

* S01–S03: student identity, Lightspeed evidence, Gitea fullstack source.
* S04–S05: native GitOps Create Application and initial resource tree.
* S06–S09: resources, BuildConfig, MongoDB PVC and populated park data.
* S10–S11: Gitea commit followed by auto-sync (no Sync button).
* S12: RBAC and two independent running stacks.

Checklist: content/modules/ROOT/images/MODULE02-SCREENSHOTS.md.
Do not change an image reference to PNG until the real image exists.
Redact passwords, Tokens and Secret values.

**Modules 3 and 5 must treat the full stack as GitOps-owned.** Direct
console changes to its Deployments or Services can be reverted by
Self-Heal. Review later modules before delivering the entire workshop.

**Not yet live-tested by this branch:** the full-stack run must pass
with two student accounts, then verify all student Gitea copies are
current. Only then mark Module 2 ready.
