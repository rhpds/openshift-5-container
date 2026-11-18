# Module 2 full-stack GitOps — Implementation and operations runbook

This is the **main Module 2 deployment**. In approximately 45 minutes,
students use the GA OpenShift GitOps console plug-in to deploy the
independent ParksMap + Python API + MongoDB 8 stack in each student's
`user-<guid>-gitops` namespace without touching Module 1's
`user-<guid>-demo` workloads. The namespace itself is created by the
**privileged tenant GitOps bootstrap** (already merged upstream);
the Argo CD instance and student Application are deployed only after the Namespace exists. The student's Kustomize tree does NOT create a Namespace.

## Source structure

The student Gitea repository (`openshift-5-container-workspace`) is flat and
mirrors this repository's examples directory. The lab content, automation and
screenshots are **not** copied to students.

```text
national-parks/
├── kustomization.yaml                 # DEFAULT entry point: the seven manifests below
├── national-parks-gitops-info.yaml    # ConfigMap edited in Module 2
├── 00-mongodb-credentials.yaml        # ServiceAccount, Role, Binding, one-time Job
├── 01-mongodb.yaml                    # ConfigMap, PVC, MongoDB 8, Service
├── 02-nationalparks-backend.yaml      # ImageStream, BuildConfig, Deployment, Service, Route
├── 03-parksmap-discovery.yaml         # discovery ServiceAccount + read-only RBAC
├── 04-parksmap-frontend.yaml          # Deployment, Service, Route
└── 05-park-data-bootstrap.yaml        # PostSync data-loading Job
weathernow/
├── kustomization.yaml                 # Module 4/5 Application source
└── weathernow.yaml                    # Deployment, Service, Route
```

The Application YAML examples stay in this repository under
`docs/instructor/applications/`; they are templates only and are not
published to students.

All 3 Deployments, 3 Services, 2 HTTPS Routes, the BuildConfig/ImageStream,
database storage and ConfigMap resources are Git-managed. Two support Jobs
handle credentials and park-data seeding.

**Legacy ParksMap startup ordering:** ParksMap's old endpoint watcher
dereferences missing or empty Endpoints objects and crashes with
`NullPointerException`. Label only `Service/nationalparks` as
`type: parksmap-backend` for discovery; the public Route remains named
`national-parks-app` without this label, because there is no
`Endpoints/national-parks-app`. The backend Deployment uses sync wave 1;
ParksMap Deployment uses sync wave 2 so it does not start before the
Service/nationalparks endpoints become ready. Do not fix this by raising
the quota or relaxing readiness checks.

**No database passwords or sample Secret manifests are committed to Git.**
The namespace-local bootstrap Job obtains random passwords from
`/dev/urandom` and creates the `nationalparks-mongodb-parameters`
Secret once. It runs with a dedicated ServiceAccount that can create
Secrets and read only that one Secret in its own namespace. Verify that
`registry.redhat.io/openshift4/ose-cli:latest` is pullable with the
cluster's configured pull secret before delivering Module 2.
The database has a 1Gi PVC using the default StorageClass. This is
disposable lab data, not a production-grade MongoDB installation.

## Provisioning and migration guard

The AgnosticV tenant workload (`ocp4_workload_tenant_namespace`, `gitops`
suffix) creates `user-<guid>-gitops` with the student's `admin` RoleBinding
and the `openshift.io/requester` annotation. The privileged bootstrap then
deploys `ArgoCD/argocd` in wave 0 *in that same namespace*.
The students create the `national-parks-settings` Application CR in
the existing `-gitops` namespace through the GitOps console.
This namespace is already created automatically for each student;
no manual *Import YAML* or *Create Project* step is part of the lab.
If it is absent, investigate and reconcile the privileged tenant
bootstrap rather than manually creating a replacement.

This changes the location of the *Argo CD instance itself*.
**Do not apply the changed bootstrap blindly to existing running
tenants.** An existing `-demo` Argo CD instance or Application may own
PVCs and Deployments. Rebuild a disposable tenant with the new layout
or follow a separately reviewed, non-destructive migration plan;
never create a second Application controlling the same live workloads.

## Preflight (instructor, before students change their Application)

```bash
USER_NAME=user-xtm9x
NS="${USER_NAME}-gitops"
ARGO_NS="${USER_NAME}-gitops"

oc get ns "$NS"
oc get ns "$NS" -o jsonpath='{.metadata.annotations.openshift\.io/requester}{"\n"}'
oc get storageclass
oc get rolebinding -n "$NS"
oc get argocd argocd -n "$ARGO_NS"
oc auth can-i get configmaps -n "$NS" --as="$USER_NAME"
```

Expected: existing `user-xtm9x-gitops`, requester annotation `user-xtm9x`, an `admin-user-xtm9x` RoleBinding, default StorageClass, and the Argo CD instance **in the same project**. No cross-namespace managed-by label is required.

Check registry pull permissions, build strategy support, resources/quota,
and the existing Gitea repository branch before class. Run the complete workshop on **two** disposable student instances
before declaring the module ready. Verify build times fit its 45-minute budget.

## Important: pre-provisioned Gitea repos are editable COPIES

Existing student Gitea repositories were imported from GitHub, **not**
configured as mirrors. Changing the upstream GitHub repository does **not**
update an existing student's Gitea clone automatically.

After merging the changes upstream, the instructor must update the whole flat
workspace tree in every existing student Gitea clone. Preserve unrelated
student work and do not force-push.
The initial workshop-wide bulk sync on 13 November 2026 returned
AUTH_FAILED on all ten Gitea pushes; verify successful write
credentials before class:

```bash
git clone https://gitea-user-xtm9x-demo.apps.ocp.dzzzx.sandbox3311.opentlc.com/user-xtm9x/openshift-5-container-workspace.git
cd openshift-5-container-workspace
git remote add workshop https://github.com/rhpds/openshift-5-container-workspace.git
git fetch workshop main
git checkout workshop/main -- national-parks/ weathernow/
git add -- national-parks/ weathernow/
git commit -m "Refresh flat GitOps workspace source"
git push origin main
```

Before this update merges upstream, fetch the current working branch
instead of workshop/main. Use only an instructor-controlled test
student and never distribute clone credentials.

**Release change:** `national-parks/kustomization.yaml` lists the seven
National Parks manifests directly. Any **already auto-syncing** Application
targeting `national-parks`, or `national-parks-settings` pointing at that path,
deploys the full stack without an additional source path switch. Schedule the
repository update only after the instructor preflight passes for that tenant.

## Create or update the Module 2 Application with Auto-Sync

Open **OCP Console → GitOps → Applications**. Select project
`user-xtm9x-gitops`, open `national-parks-settings`, then **Edit YAML**
(or use `oc apply -f` with the file below).

Use [national-parks-application-example.yaml](../../docs/instructor/applications/national-parks-application-example.yaml).
Its `repoURL`, Application namespace and destination are specific to
`user-xtm9x`; substitute the actual student's Gitea clone URL for
other lab instances.

Important settings:

- `spec.source.path: national-parks`
- `spec.destination.namespace: user-xtm9x-gitops`
- `spec.syncPolicy.automated.enabled: true`; selfHeal true; prune false
- `ignoreDifferences` for **only** the backend Deployment container image
  and `RespectIgnoreDifferences=true`

The image exception is necessary: the OpenShift BuildConfig builds
`nationalparks-py` from source to `ImageStreamTag/nationalparks:latest`,
and the OpenShift image trigger rewrites the Deployment's container image.
Without the narrow exception, Argo CD self-heal could revert the
ImageStream-triggered digest. Do not ignore arbitrary Deployment fields.

## Verify

```bash
ARGO_NS=user-xtm9x-gitops
NS=user-xtm9x-gitops

oc -n "$ARGO_NS" get application national-parks-settings \\
  -o jsonpath='{.spec.source.path}{"\n"}{.status.sync.status}{" / "}{.status.health.status}{"\n"}'
oc -n "$NS" get job,pvc,buildconfig,imagestream
oc -n "$NS" get deployment parksmap nationalparks mongodb-nationalparks
oc -n "$NS" get service parksmap nationalparks mongodb-nationalparks
oc -n "$NS" get route parksmap national-parks-app
oc -n "$NS" get secret nationalparks-mongodb-parameters -o name
oc -n "$NS" get deployment nationalparks \\
  -o jsonpath='{.spec.template.spec.containers[0].image}{"\n"}'
```

The Python BuildConfig creates the image locally. A temporary
`ImagePullBackOff` on `nationalparks` before the first build publishes
its ImageStreamTag can occur; after the build finishes, verify the
image change trigger updates the Deployment image. If it does not,
inspect the BuildConfig and Deployment's
`image.openshift.io/triggers` annotation. **Do not manually patch the
Deployment image in an auto-syncing GitOps application.**

The MongoDB Service uses port **27017**, not Module 1's deliberately
broken 27018. The Python API uses the namespace-local MongoDB Service
and obtains the same database credentials through a Secret reference.
After workloads are healthy, a `PostSync` Job checks `/ws/data/all`
and calls `/ws/data/load` only if the returned JSON collection is
empty. Since `/ws/data/load` DELETES and reloads data, do not call it
repeatedly as a health check or use this module against real data.

Discover the new route hosts dynamically:

```bash
oc -n "$NS" get route parksmap -o jsonpath='https://{.spec.host}{"\n"}'
oc -n "$NS" get route national-parks-app -o jsonpath='https://{.spec.host}{"/ws/data/all"}{"\n"}'
curl -fsS "https://$(oc -n "$NS" get route national-parks-app -o jsonpath='{.spec.host}')/ws/data/all" | head -c 300
```

The backend should return a **nonempty JSON list of park records**,
and the ParksMap UI should show markers. If data is empty, inspect
`Job/nationalparks-seed-data` status and logs; the PostSync hook may
not run until the sync is healthy. Do not expose generated credentials
in logs, screenshots, or Lightspeed prompts.

## Acceptance boundaries

- No Namespace YAML in the student's Kustomize tree (bootstrap owns it).
- Module 1 workloads stay untouched in `user-<guid>-demo`.
- `national-parks/kustomization.yaml` deploys the seven National Parks manifests.
- No static database passwords in Git or ConfigMaps.
- No cluster-wide RBAC; ParksMap has read-only Services/Routes discovery.
- GitOps self-heal does not fight OpenShift image-trigger updates.
- PVC requires a working default StorageClass.
- Auto-prune stays disabled; Git commits reconcile automatically without manual Sync.

This implementation is **source-controlled but not yet live-validated**. Two real student rehearsals and an audited update of all student Gitea copies are required before delivery.
