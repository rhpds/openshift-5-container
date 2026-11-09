# Module 1: native console deployment preflight

This checklist accompanies the new **25-minute Mission National Parks**. Students
deploy `parksmap` from an image and `nationalparks` from Git in the OpenShift 5
console, then import `module01-mongodb.yaml`. It is a **deployment rehearsal
contract, not proof the target cluster has been tested**.

## Prerequisites to verify before advertising a 25-minute runtime

1. Each student can access their existing **`user-<GUID>-demo`** project in
   the console. **No student namespace creation is part of Module 1.** The
   screenshot S00 correctly shows `user-pjbsb-demo` as one example. Students
   must not use `default`, `user-<GUID>` or another student's project.
2. Check that `user-<GUID>-demo` does not yet contain the National Parks
   Deployments, Services or Routes. This namespace can already host Argo CD,
   Gitea and Showroom services; **do not clean it up** to make it empty.
3. As a real student identity, confirm permission to create Deployments,
   Services, Routes, ImageStreams and BuildConfigs; edit the application's
   Deployment YAML; read workloads and build logs; and import YAML.
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
   A slow or failed Dockerfile build makes a 25-minute end-to-end promise
   unrealistic; prepare a documented fallback.
6. Verify the tutorial MongoDB image in
   `content/modules/ROOT/examples/module01-mongodb.yaml` can be pulled
   with the workshop's registry credentials, runs with arbitrary OpenShift
   UIDs and supports the `MONGODB_*` Secret keys and data mount. This image
   choice is **not yet validated for the target OCP 5 cluster**. Replace it
   with a tested compatible image and adjust the YAML if necessary.
7. Provide a Secret named `nationalparks-mongodb-parameters` in every student
   **`user-<GUID>-demo` project**; do not store its password in Git, screenshots or AI
   prompts. For a disposable, isolated namespace, an administrator may create
   it with `oc create secret generic` using generated values for
   `MONGODB_USER`, `MONGODB_PASSWORD`, `MONGODB_DATABASE`,
   `MONGODB_ADMIN_PASSWORD` and `DATABASE_SERVICE_NAME`. **This is a required
   instructor setup step, not a resource created by `module01-mongodb.yaml`.**
8. The original parksmap discovery app needs permission to list project
   services/routes. The vendor tutorial uses a namespace-scoped `view`
   RoleBinding for the default service account; test that arrangement under
   the student's identity in **`user-<GUID>-demo`**. Because this namespace
   also hosts workshop services, grant only the minimal reads needed for
   discovery and avoid exposing unrelated Secrets. A dedicated least-privilege
   frontend account is preferable. Do **not** grant cluster-admin.
9. Confirm the `nationalparks` **Route** (not just its Deployment) has label
   `type=parksmap-backend`, and the backend can access MongoDB after its
   Deployment adds `envFrom.secretRef` for the prepared Secret.
10. Test exactly one initial `GET /ws/data/load` on **disposable** data, then
    verify `GET /ws/data/all` is a nonempty array and the map has markers.
    Loading is destructive/reinitializing; never use it for health checks.
11. Verify the OpenShift Lightspeed MCP read tools under a student identity;
    require successful tool evidence rather than the assistant's assertion.
12. Rehearse with **two student accounts**, capture the actual OCP 5 console
    screens, and time the whole lab. Only then call the lab 25 minutes.
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

- Ensure the instructor-prepared MongoDB Secret and discovery RBAC exist in
  **that exact namespace**, not the separate `user-<GUID>` namespace created
  by the bootstrap templates.
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

## Provision the MongoDB Secret before students begin

Run this once **per student demo namespace** as an instructor or administrator.
Replace the example namespace with the student's actual `user-<GUID>-demo`.
The two passwords are generated independently; do not replace them with the
well-known passwords from the original tutorial. Do not put the generated
values in Git, slides, screenshots or support tickets.

```bash
LAB_NAMESPACE=user-REPLACE_WITH_STUDENT-demo

oc get namespace "$LAB_NAMESPACE"
oc get secret nationalparks-mongodb-parameters -n "$LAB_NAMESPACE" -o name
```

If the last command succeeds, **keep the existing Secret**. Do not overwrite
or regenerate its credentials: that can break an already-initialized database.
If it returns `NotFound`, create the Secret in that exact namespace:

```bash
oc create secret generic nationalparks-mongodb-parameters \
  -n "$LAB_NAMESPACE" \
  --from-literal=DATABASE_SERVICE_NAME=mongodb-nationalparks \
  --from-literal=MONGODB_USER=mongodb \
  --from-literal=MONGODB_PASSWORD="$(openssl rand -hex 20)" \
  --from-literal=MONGODB_DATABASE=mongodb \
  --from-literal=MONGODB_ADMIN_PASSWORD="$(openssl rand -hex 20)"

oc get secret nationalparks-mongodb-parameters -n "$LAB_NAMESPACE" -o name
```

If the initial check fails for any reason **other than `NotFound`** (for
example, missing permissions), resolve that problem before attempting to
create the Secret. Repeat the setup for every assigned student namespace.
The same Secret is consumed by the `mongodb-nationalparks` Deployment and the
`nationalparks` backend's `envFrom.secretRef`, so the name and namespace must
match exactly. Rehearse the MongoDB image and connection with these keys;
creating the Secret alone does not prove the database image works on OCP 5.

In the student mission, *Workloads → Secrets* is a **name-only prerequisite
check** in Mission 0 and again before Mission 3. If students cannot list
Secrets under their assigned RBAC, the instructor must confirm its existence
without revealing the values. A missing Secret causes pod events such as
`secret "nationalparks-mongodb-parameters" not found` and blocks the backend
rollout; adding `envFrom` does not create a Secret.

## Instructor smoke test (read-only; set the actual namespace)

```bash
LAB_NAMESPACE=user-REPLACE_WITH_STUDENT-demo

oc get namespace "$LAB_NAMESPACE"
oc get deploy,svc,route -n "$LAB_NAMESPACE" | head -30
oc get secret nationalparks-mongodb-parameters -n "$LAB_NAMESPACE" -o name
oc auth can-i create deployments.apps -n "$LAB_NAMESPACE" --as=REPLACE_WITH_STUDENT_USER
oc auth can-i create buildconfigs.build.openshift.io -n "$LAB_NAMESPACE" --as=REPLACE_WITH_STUDENT_USER
oc auth can-i create routes.route.openshift.io -n "$LAB_NAMESPACE" --as=REPLACE_WITH_STUDENT_USER
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
