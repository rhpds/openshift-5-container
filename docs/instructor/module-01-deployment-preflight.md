# Module 1: native console deployment preflight

This checklist accompanies the new **25-minute Mission National Parks**. Students
deploy `parksmap` from an image and `nationalparks` from Git in the OpenShift 5
console, then import `module01-mongodb.yaml`. It is a **deployment rehearsal
contract, not proof the target cluster has been tested**.

## Prerequisites to verify before advertising a 25-minute runtime

1. Each student can access their **application** project (`user-<GUID>`), not
   only the separate `user-<GUID>-demo` project. The supplied S00 capture
   currently shows only `-demo`; recapture it after verifying access.
2. Each application project starts without National Parks Deployments, Services
   or Routes. Do not delete unrelated student resources to make it empty.
3. As a real student identity, confirm permission to create Deployments,
   Services, Routes, ImageStreams and BuildConfigs; edit the application's
   Deployment YAML; read workloads and build logs; and import YAML.
4. Verify `quay.io/openshiftroadshow/parksmap:latest` pulls and produces a
   reachable Route in the student namespace. Pin an immutable digest after
   validation; the tutorial's moving `latest` is not an immutable workshop
   contract.
5. Rehearse *Import from Git* of
   `https://github.com/openshift-roadshow/nationalparks-py.git` using a
   Python 3.12-compatible builder. Capture the detected import strategy,
   successful build and total build time. A slow/missing builder makes a
   25-minute end-to-end promise unrealistic; prepare a documented fallback.
6. Verify the tutorial MongoDB image in
   `content/modules/ROOT/examples/module01-mongodb.yaml` can be pulled
   with the workshop's registry credentials, runs with arbitrary OpenShift
   UIDs and supports the `MONGODB_*` Secret keys and data mount. This image
   choice is **not yet validated for the target OCP 5 cluster**. Replace it
   with a tested compatible image and adjust the YAML if necessary.
7. Provide a Secret named `nationalparks-mongodb-parameters` in every student
   application namespace; do not store its password in Git, screenshots or AI
   prompts. For a disposable, isolated namespace, an administrator may create
   it with `oc create secret generic` using generated values for
   `MONGODB_USER`, `MONGODB_PASSWORD`, `MONGODB_DATABASE`,
   `MONGODB_ADMIN_PASSWORD` and `DATABASE_SERVICE_NAME`.
8. The original parksmap discovery app needs permission to list project
   services/routes. The vendor tutorial uses a namespace-scoped `view`
   RoleBinding for the default service account; test that arrangement under
   the student's identity. A dedicated least-privilege frontend account is
   preferable for a production scenario. Do **not** grant cluster-admin.
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

## Instructor smoke test (read-only; set the actual namespace)

```bash
LAB_NAMESPACE=user-REPLACE_WITH_STUDENT

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
