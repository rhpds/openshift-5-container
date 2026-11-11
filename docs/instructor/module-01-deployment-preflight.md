# Module 1: native console deployment preflight

This checklist accompanies the **50-minute Mission National Parks**. Students
deploy `parksmap` from an image and `nationalparks` from Git in the OpenShift 5
console, create their own MongoDB Secret, then import `module01-mongodb.yaml`.
The manifest deliberately deploys MongoDB 3.2.10 so students can diagnose
PyMongo 4.18.1 incompatibility through **Lightspeed 2.0 Troubleshooting** and
apply a reviewed **image-only** fix themselves in the console to MongoDB 8.0.32. This is a **rehearsal contract, not proof the target cluster has
been tested**.

## Prerequisites to verify before advertising a 50-minute runtime

Before students begin, verify OpenShift Lightspeed Operator **2.0.0** and a
healthy OLSConfig. The Operator Subscription should use the supported
`redhat-operators` catalog rather than the workshop's historical catalog pinned
to Lightspeed 1.1.4. Operator installation/version selection belongs to the
cluster provisioning owner, not this Showroom content repository.

```bash
oc get csv -n openshift-lightspeed
oc get subscription lightspeed-operator -n openshift-lightspeed \
  -o jsonpath='{.spec.source}{" "}{.status.installedCSV}{"\n"}'
oc get olsconfig cluster -o jsonpath='{.status.overallStatus}{"\n"}'
```

Expect the intended `lightspeed-operator.v2.0.0` CSV to be `Succeeded`, the
OLSConfig to be `Ready`, and Troubleshooting mode to produce successful live
Kubernetes MCP **read** results with the student identity. Neither MCP write
tools nor the separate Agentic Lightspeed component is required for Module 1.

1. Each student can access their existing **`user-<GUID>-demo`** project in
   the console. **No student namespace creation is part of Module 1.** The
   screenshot S00 correctly shows `user-pjbsb-demo` as one example. Students
   must not use `default`, `user-<GUID>` or another student's project.
2. Check that `user-<GUID>-demo` does not yet contain the National Parks
   Deployments, Services or Routes. This namespace can already host Argo CD,
   Gitea and Showroom services; **do not clean it up** to make it empty.
3. As a real student identity, confirm permission to create ConfigMaps,
   Deployments, Services, Routes, **Secrets**, ImageStreams and BuildConfigs;
   edit the application's Deployment YAML; read workloads and build logs;
   and import YAML. Students must be able to list their own Secret by name.
   Confirm **Lightspeed 2.0 built-in MCP** can read Pod logs under the student's
   identity and that the student can manually update the named Deployment in
   the console. Generic MCP write tools are not required (see below).
4. Verify `quay.io/openshiftroadshow/parksmap:latest` pulls and produces a
   reachable Route in `user-<GUID>-demo`. Pin an immutable digest after
   validation; the tutorial's moving `latest` is not an immutable workshop
   contract.
5. Rehearse *Import from Git* of
   `https://github.com/openshift-roadshow/nationalparks-py.git`. Keep the
   repository's recommended Dockerfile, which uses UBI 9 Python 3.12; select
   *BuildConfig* for the build and *Deployment* for the runtime resource.
   Verify the Build completes and its log ends in a successful image push,
   then verify the backend Pod is Running and its Route displays
   `Welcome to the National Parks data service.`. Capture total build time.
   A slow or failed Dockerfile build makes a 50-minute end-to-end promise
   unrealistic; prepare a documented fallback.
6. Verify **both** image references from the manifest work in the target OCP 5
   cluster as the student: initially `registry.redhat.io/rhmap47/mongodb`
   (the deliberate **3.2.10** fault), then
   `quay.io/mongodb/mongodb-community-server:8.0.32-ubi9-slim`
   (the target **8.0.32** image). Check registry access, arbitrary OpenShift
   UIDs, `emptyDir` mounts at both image data paths and the bootstrap ConfigMap
   mount. The ConfigMap's `create-app-user.js` must run on the *new* image and
   create the user specified by the student's Secret. Confirm the backend
   reports PyMongo 4.18.1, old MongoDB logs show `cannot translate opcode 2013`
   and new MongoDB logs report successful bootstrap and no authentication
   failure. **This version-switch/bootstrap flow has not yet been validated on
   the target OCP 5 cluster; do not advertise it as tested.**
7. **Do not pre-create the National Parks database Secret for students.**
   Each student creates `nationalparks-mongodb-parameters` in their own
   **`user-<GUID>-demo`** project using *Workloads → Secrets → Create →
   Key/value secret*. Rehearse entering all five expected keys under a
   student identity. They must use their own separate passwords for
   `MONGODB_PASSWORD` and `MONGODB_ADMIN_PASSWORD`, without storing values
   in Git, screenshots or AI prompts. The prepared `module01-mongodb.yaml`
   deliberately does **not** create this Secret.
8. Apply and test the **rendered Showroom** YAML from
   `content/modules/ROOT/examples/module01-parksmap-discovery.yaml`
   in **`user-<GUID>-demo`**. AsciiDoc substitutes `{user}` in the RoleBinding
   namespace automatically; the raw repository YAML is a template and must
   be rendered before applying directly with `oc`. The dedicated
   `parksmap-discovery` ServiceAccount needs Route and Service `get/list/watch`
   plus named backend Endpoint `get/watch` access. Confirm the ParksMap Pod
   runs under this ServiceAccount and its logs contain no Endpoint `Forbidden`
   errors. Do **not** grant `view` to `default`, access to Secrets or cluster-admin.
9. Confirm the `nationalparks` **Route** (not just its Deployment) has label
   `type=parksmap-backend`, and the backend can access MongoDB after its
   Deployment adds `envFrom.secretRef` for the student-created Secret.
10. Confirm `GET /ws/data/all` fails *before* the upgrade, then returns an
    empty list after the console image change. Only **after** that change, test one
    initial `GET /ws/data/load` on disposable data, verify `/ws/data/all`
    becomes nonempty and the map has markers. Loading is destructive;
    never use it for health checks.
11. Verify **Lightspeed 2.0 Troubleshooting** can call live Kubernetes MCP
    **read tools** under a student identity. Approval dialogs are optional:
    when policy requires them, confirm the student can review and approve only
    namespace-scoped read operations; when reads are automatic, verify the
    resulting answer actually contains live evidence from the correct project.
    The ParksMap discovery RoleBinding does not govern MCP tool approvals.
    Capture evidence of MongoDB opcode failures and the Python connection
    error. The tested built-in toolset did **not** expose
    `resources_create_or_update`, `resources_scale` or `resources_delete`, even
    with `read_only = false`. Students must **manually edit only the MongoDB
    container image** through the console. Check the resulting Deployment,
    Pod readiness and logs. A confident chatbot answer alone does not count.
12. Rehearse with **two student accounts**, capture the actual OCP 5 console
    screens, and time the whole lab. Only then call the lab 50 minutes.
13. The current `parksmap-web` frontend hard-codes *Map Visualizer on OpenShift 4*
    in `src/main/resources/static/index.html`. That text is not a cluster
    version check. Its geolocation promise currently lacks an error/rejection
    callback, so denying browser location access can prevent backend map-layer
    updates. Rehearse both permission choices and provide an alternative if
    students do not wish to share their location. The workshop currently uses
    the existing `quay.io/openshiftroadshow/parksmap:latest` image; no
    OpenShift 5-specific replacement has been validated.

## Existing workshop project (not a new namespace)

The student selects **`user-<GUID>-demo`**. This deliberately reuses a project
that may also contain Argo CD, Gitea and Showroom resources. Before class:

- Ensure students can **create Secrets** and discovery RBAC exists in
  **that exact namespace**, not the separate `user-<GUID>` namespace created
  by the bootstrap templates. The National Parks database Secret should be
  **absent before a fresh lab**, so students can create it themselves.
- Verify the student has enough quota/resources to run the three National
  Parks workloads *alongside* the existing workshop services.
- Verify the required frontend service discovery permissions and backend
  visibility work in this populated namespace without overprivileging the
  default service account.
- Ensure no GitOps Application or automation will prune, overwrite, or adopt
  the manually created National Parks resources unexpectedly.

The older instruction to create or select `user-<GUID>` is removed. The S00b
*Create Project* screenshot is no longer part of the student module. The new
S05b–S05e screenshots cover the frontend image form, while S06a–S06i
cover the backend Dockerfile build, logs and Route check.

## Rehearse student-created MongoDB Secrets

Students create the Secret in **Mission 3**, before importing the MongoDB
ConfigMap, Deployment and Service. In *Workloads → Secrets*, select *Create → Key/value
secret*, then enter the name `nationalparks-mongodb-parameters` and these
five keys:

| Key | Student value |
| --- | --- |
| `DATABASE_SERVICE_NAME` | `mongodb-nationalparks` |
| `MONGODB_USER` | `mongodb` |
| `MONGODB_DATABASE` | `mongodb` |
| `MONGODB_PASSWORD` | Student-chosen unique password, at least 16 letters/digits |
| `MONGODB_ADMIN_PASSWORD` | Different student-chosen unique password, at least 16 letters/digits |

Students select *Create*, verify the Secret name in the list, then import
`module01-mongodb.yaml` and edit the backend Deployment's `envFrom.secretRef`.
The same Secret is used by both workloads. MongoDB 8 uses
`MONGODB_ADMIN_PASSWORD` as its root password (through `MONGO_INITDB_ROOT_PASSWORD`),
while `mongodb-nationalparks-bootstrap` reads the application username and
password from its environment to create a restricted `readWrite` user. The
name and namespace must match
exactly. **Do not screenshot or collect password values.**

Before class, check Secret-creation permissions using an actual student
account and rehearse the entire flow. A fresh project should not already
contain `nationalparks-mongodb-parameters`. If it does, identify whether it
belongs to a previous rehearsal or a running database; **do not overwrite,
rotate or delete it blindly**, because this can break that workload. Coordinate
a deliberate workshop reset where required. A missing Secret causes pod events
such as `secret "nationalparks-mongodb-parameters" not found` and blocks the
backend rollout; adding `envFrom` alone does not create the Secret.

## Reset an existing National Parks database lab for another attempt

Use this **only** when a student has already completed Module 1 and wants to
repeat the deliberate MongoDB failure and Lightspeed recovery. It changes the
three named MongoDB workshop resources and replaces the database Pod, thereby
discarding its `emptyDir` data. **Do not use it for a persistent database.**
Confirm the namespace and that its MongoDB resources belong to this disposable
exercise first. Never reset the whole namespace or modify the student's Secret.

From the repository root, for the example project `user-pjbsb-demo`:

```bash
# Inspect the intended target before modifying it.
oc -n user-pjbsb-demo get deployment/mongodb-nationalparks service/mongodb-nationalparks
oc -n user-pjbsb-demo get configmap/mongodb-nationalparks-bootstrap --ignore-not-found

# Reapply only the prepared ConfigMap, Deployment and internal Service.
# The Deployment image is intentionally reset to the old 3.2.x image.
oc -n user-pjbsb-demo apply -f content/modules/ROOT/examples/module01-mongodb.yaml
oc -n user-pjbsb-demo rollout status deployment/mongodb-nationalparks

# Verify the actual live image and prepared modern-image prerequisites.
oc -n user-pjbsb-demo get deployment/mongodb-nationalparks \
  -o jsonpath='{.spec.template.spec.containers[?(@.name=="mongodb")].image}{"\n"}'
oc -n user-pjbsb-demo get configmap/mongodb-nationalparks-bootstrap
oc -n user-pjbsb-demo logs deployment/mongodb-nationalparks --tail=30
```

Replace `user-pjbsb-demo` with the **exact project being reset**; never run
against all namespaces. The image must report
`registry.redhat.io/rhmap47/mongodb`. Confirm the old server really starts as
MongoDB **3.2.10** from its logs before demonstrating the expected `opcode 2013`
failure. The repository does not pin the old image by immutable digest, so a
registry change would require revalidation rather than assuming the server
version from the image name alone.

The original Secret `nationalparks-mongodb-parameters`, backend Deployment,
parksmap and Routes stay in place. A returning student skips the *Create* and
*Import YAML* steps that already succeeded, starts with the broken-data check
at the end of Mission 3, and continues in *Lightspeed → Troubleshooting*.

**Image-only recovery contract:** For the new Community Server image the
prepared Deployment already maps `MONGODB_ADMIN_PASSWORD` to
`MONGO_INITDB_ROOT_PASSWORD`, sets `MONGO_INITDB_ROOT_USERNAME` and
`MONGO_INITDB_DATABASE`, and mounts an `emptyDir` at `/data/db` plus the
bootstrap ConfigMap at `/docker-entrypoint-initdb.d`. The JavaScript creates
the application user from the student's existing `MONGODB_USER` and
`MONGODB_PASSWORD` variables. Do not ask Lightspeed to invent a second image
family or change these settings. Loading park records through `/ws/data/load`
is a **deliberate later student step**, not a missing bootstrap prerequisite.

This manifest structure can be validated without a cluster using
`python3 -m unittest discover -s tests -p 'test_module01_mongodb_recovery.py'`
(requires PyYAML). This is **not** a substitute for the live two-image
OpenShift smoke test above.

## Instructor smoke test (read-only; set the actual namespace)

```bash
LAB_NAMESPACE=user-REPLACE_WITH_STUDENT-demo

oc get namespace "$LAB_NAMESPACE"
oc get deploy,svc,route -n "$LAB_NAMESPACE" | head -30
oc auth can-i create deployments.apps -n "$LAB_NAMESPACE" --as=REPLACE_WITH_STUDENT_USER
oc auth can-i create buildconfigs.build.openshift.io -n "$LAB_NAMESPACE" --as=REPLACE_WITH_STUDENT_USER
oc auth can-i create routes.route.openshift.io -n "$LAB_NAMESPACE" --as=REPLACE_WITH_STUDENT_USER
oc auth can-i create secrets -n "$LAB_NAMESPACE" --as=REPLACE_WITH_STUDENT_USER
oc auth can-i list secrets -n "$LAB_NAMESPACE" --as=REPLACE_WITH_STUDENT_USER
oc auth can-i create configmaps -n "$LAB_NAMESPACE" --as=REPLACE_WITH_STUDENT_USER
oc auth can-i get pods/log -n "$LAB_NAMESPACE" --as=REPLACE_WITH_STUDENT_USER
oc auth can-i patch deployments.apps -n "$LAB_NAMESPACE" --as=REPLACE_WITH_STUDENT_USER
oc auth can-i update deployments.apps -n "$LAB_NAMESPACE" --as=REPLACE_WITH_STUDENT_USER
```

Do not use the admin `--as` smoke test as proof of all student browser UI
permissions. Log in as two real students, verify their available projects,
perform the full Import from Git and MongoDB image pull, and capture the
Screenshots guide evidence.

## Handoff to Module 2

The current Module 2 assumes GitOps already owns the whole app. That assumption
**no longer holds** after this native-console Module 1. Before delivering
Module 2, prepare and test a Git source of truth that **matches the resources
created in Module 1** and an Argo CD onboarding/reconciliation workflow that
does not accidentally replace the running app or delete its data. Do not enable
auto-prune or self-heal during initial adoption without a verified dry run.

## References

- [Red Hat: National Parks console tutorial (4.22 baseline)](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/tutorials/dev-app-web-console)
- [National Parks Python backend source](https://github.com/openshift-roadshow/nationalparks-py)
- [Module 1 student source](../../content/modules/ROOT/pages/module-01-whats-new-in-ocp5.adoc)
- [MongoDB YAML resource](../../content/modules/ROOT/examples/module01-mongodb.yaml)
- [Screenshot specifications](../../content/modules/ROOT/images/SCREENSHOTS.md)
