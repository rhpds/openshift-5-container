# Module 1 instructor preflight: Service selector troubleshooting

Students deploy ParksMap, Python National Parks and **working MongoDB 8**.
After loading park records, they deliberately change the Python backend
**Service** selector (`spec.selector.app`) to `intentionally-broken-backend`.
Lightspeed 2.0 reads live Pods, Services and Routes to diagnose the missing
endpoints. Students restore the selector in the console. **No MCP write tools
or MongoDB image updates are required.**

## Before class

1. Verify the student is logged in as `user-<guid>` and working in
   `user-<guid>-demo` (not the Showroom service account).
2. Check that Argo CD and Gitea already exist in the project. **Do not
   delete them**, and make sure Argo CD is not automatically reconciling
   the student-created National Parks resources.
3. Check permissions to create Secrets, ConfigMaps, Deployments, Services,
   Routes and the ParksMap discovery Role/RoleBinding, plus permission to
   **edit the backend Service** and read Kubernetes resources with Lightspeed.
4. Verify the ParksMap image can pull, the `nationalparks-py` Dockerfile
   builds, and the MongoDB 8 image
   `quay.io/mongodb/mongodb-community-server:8.0.32-ubi9-slim` starts.
   MongoDB uses disposable `emptyDir` storage and a per-student Secret.
5. Verify `parksmap` uses `serviceAccountName: parksmap-discovery` and
   backend Service and Route both have `type=parksmap-backend`.
6. Load disposable data by visiting the backend `/ws/data/load` **once**.
   Confirm `/ws/data/all` contains records **before breaking connectivity**.
7. Record the **actual backend Service name** (`nationalparks` or
   `national-parks-app`), its `spec.selector`, and matching Pod labels.
   Test the one-value change below using a fresh student. Do not modify the
   MongoDB Service or Deployment.

## Rehearse the fault and repair

In the backend Service YAML, replace **only** the existing
`spec.selector.app` value:

```yaml
spec:
  selector:
    app: intentionally-broken-backend
```

Keep other selector entries unchanged. The backend Service should have no
matching endpoints, while the Python Pod remains Running and its Route
stops serving the backend.

Run the short read-only Lightspeed prompt in Mission 4. Require live evidence
of the mismatched Service selector and backend Pod labels. The student then
restores `spec.selector.app` to the value recorded from the matching Pods.
Verify:

- Backend Route `/ws/data/all` returns nonempty park data.
- ParksMap `/ws/backends/list` finds the Python backend.
- The map displays park markers.

The Service fault is repeatable without deleting Pods, Secrets or data.
**Do not reset the whole student namespace.**

## Limitations

- This is a static manifest contract, not a completed live-cluster smoke test.
  Rehearse with two fresh student accounts.
- The built-in Lightspeed 2.0 MCP deployment may provide read tools only;
  students use the OpenShift console for the Service update.
- Keep Argo CD auto-sync disabled before Module 2 onboarding; otherwise
  GitOps could immediately reverse the deliberate fault.
- Existing tenant quotas include Argo CD and Gitea. Do not introduce an
  additional restrictive quota in Module 1.

## Files

- [Student guide](../../content/modules/ROOT/pages/module-01-whats-new-in-ocp5.adoc)
- [MongoDB 8 manifest](../../content/modules/ROOT/examples/module01-mongodb.yaml)
- [ParksMap discovery RBAC](../../content/modules/ROOT/examples/module01-parksmap-discovery.yaml)
