# Module 4 — Agentic National Parks data-path incident: instructor preflight

## Purpose

This is a **40-minute, five-mission** practical follow-on to Module 3. It assumes the student has completed Module 3's ParksMap readiness repair and already has two working copies of National Parks:

- original: user-<guid>-demo
- student Gitea/Argo CD stack: user-<guid>-gitops
- Argo CD Application: national-parks-settings in user-<guid>-demo

A student introduces a **single explicit DATABASE_SERVICE_NAME override** with the value **mongodb-national-parks** (incorrect) into the backend Deployment in the student Gitea source. The Secret's correct DATABASE_SERVICE_NAME remains unchanged; Kubernetes gives explicit env priority over envFrom. The backend code in [openshift-roadshow/nationalparks-py/wsgi.py](https://github.com/openshift-roadshow/nationalparks-py/blob/master/wsgi.py) reads that variable for DB_HOST, but /ws/healthz/ does not access MongoDB. Thus all Pods can appear healthy while /ws/data/all fails.

The student uses Lightspeed Troubleshooting and direct Kubernetes evidence, optionally observes an **instructor-created analysis-only AgenticRun**, then **removes exactly the bad env block in Gitea** and proves recovery. This is a new failure mode, separate from Module 3's readiness probe mismatch and Module 1's deliberately incorrect MongoDB Service target port.

## Instructor preflight

Before students introduce any fault, verify the correct source and original app:

~~~bash
STUDENT=user-xxxxx
DEMO_NS="$STUDENT-demo"
GITOPS_NS="$STUDENT-gitops"

oc get deploy mongodb-nationalparks nationalparks parksmap -n "$DEMO_NS"
oc get deploy mongodb-nationalparks nationalparks parksmap -n "$GITOPS_NS"
oc get application national-parks-settings -n "$DEMO_NS" -o json | \
  jq '{sync: .status.sync.status, health: .status.health.status,
       revision: .status.sync.revision}'

oc get deployment parksmap -n "$GITOPS_NS" -o json | \
  jq '.spec.template.spec.containers[0].readinessProbe'
oc get deployment nationalparks -n "$GITOPS_NS" -o json | \
  jq '.spec.template.spec.containers[0] | {envFrom, explicitEnv: .env}'
oc get svc mongodb-nationalparks -n "$GITOPS_NS" -o yaml
~~~

Confirm the original Module 3 probe is **http**, both apps have the expected 3/3 healthy Deployments, and the backend has **no explicit DATABASE_SERVICE_NAME override**. The baseline API must return records before the incident:

~~~bash
API_HOST="$(oc get route national-parks-app -n "$GITOPS_NS" -o jsonpath='{.spec.host}')"
curl -fsS --max-time 25 "https://$API_HOST/ws/data/all" | \
  python3 -c 'import json,sys; a=json.load(sys.stdin); print(len(a)); assert isinstance(a,list) and len(a)>0'
~~~

The student Gitea repo is NOT a live mirror of upstream GitHub. Check its main branch, especially fullstack/02-nationalparks-backend.yaml and the rest of the Module 2 fixes. **Do not run fast-forward --sync-gitea after the deliberate bad commit**, because that option intentionally replaces the student manifest.

## Fault injection and observations

1. In student Gitea main, open content/modules/ROOT/examples/module02-gitops/fullstack/02-nationalparks-backend.yaml.
2. Add only this block after the existing envFrom in **Deployment/nationalparks** (not BuildConfig):

~~~yaml
          env:
            - name: DATABASE_SERVICE_NAME
              value: mongodb-national-parks
~~~

3. Commit using message: lab(module04): simulate National Parks database DNS misconfiguration.
4. Let Argo CD Auto-Sync. The backend Deployment's live explicit env must show the wrong value.
5. Run the API data query with an HTTP timeout and compare to /ws/healthz/ and the MongoDB Service.
6. Check the original app in -demo remains healthy and serving data. Do not touch Secrets, PV/PVC, Database, Services, ResourceQuota, Alertmanager or ApprovalPolicy.

Expected effects are **not deterministic HTTP status codes**: PyMongo's server selection can cause timeouts and Flask/Gunicorn can return 5xx, while the lightweight health handler often remains 200. Under high request concurrency, worker pressure may cause intermittent readiness failures. Never claim that GitOps will *always* remain Healthy or that /ws/data/all *always* returns 500. The reliable root-cause signal is the explicit non-existent DB hostname plus the correct namespace-local Service name.

## Agentic integration gate (instructor only)

As with Module 3, student RBAC can forbid reading/creating AgenticRuns in openshift-lightspeed while the CRD exists. It is not a student error.

~~~bash
oc get crd agenticruns.agentic.openshift.io
oc get agent default -o yaml
oc get llmprovider
oc get pods -n openshift-lightspeed
oc auth can-i create agenticruns.agentic.openshift.io -n openshift-lightspeed
oc auth can-i get agenticruns.agentic.openshift.io -n openshift-lightspeed
oc get consoleplugins -o name | grep -i agentic || true
~~~

Inspect the configured Agent/default LLM, MCP endpoints and **tool-level RBAC**, especially mutating capabilities. Omitting spec.execution and spec.verification prevents their stages but does not automatically turn all Analysis tools into read-only tools. Authorize only approved read paths for the target namespace. Do not change global ApprovalPolicy or enable alert adapters in a shared student cluster.

Once an actual student Gitea bad revision is live, run the guarded instructor script from a workshop repository checkout:

~~~bash
bash automation/scripts/create-module04-agentic-run.sh user-xxxxx

RUN_NAME=parksdata-user-xxxxx-dns
oc get agenticrun "$RUN_NAME" -n openshift-lightspeed -o yaml
~~~

The script checks the API, RBAC, Agent/default, intended namespace and the *live* deliberate env override before creating a unique analysis-only AgenticRun. It does not grant permissions, read Secret values, patch Deployments, execute remediation or schedule future runs. Demonstrate **one run at a time** across the class.

If the operator, provider, tools or permissions are missing, the module has a complete read-only Lightspeed and CLI fallback; explicitly say "AgenticRun not available/not authorized" and do not claim success. When reviewing a run, show the recorded Analysis evidence and proposed changes; the student decides whether the diagnosis agrees with live evidence.

## Recovery gate

The student **removes only the added env block** through Gitea main:

~~~yaml
          env:
            - name: DATABASE_SERVICE_NAME
              value: mongodb-national-parks
~~~

The existing envFrom.secretRef remains intact. Let Auto-Sync reconcile; validate:

~~~bash
oc get deployment nationalparks -n "$GITOPS_NS" -o json | \
  jq '.spec.template.spec.containers[0] | {envFrom, explicitEnv: .env}'
oc rollout status deployment/nationalparks -n "$GITOPS_NS" --timeout=180s
oc get application national-parks-settings -n "$DEMO_NS" -o json | \
  jq '{sync: .status.sync.status, health: .status.health.status,
       revision: .status.sync.revision}'
curl -fsS --max-time 25 "https://$API_HOST/ws/data/all" | \
  python3 -c 'import json,sys; a=json.load(sys.stdin); print(len(a)); assert isinstance(a,list) and len(a)>0'
oc get deploy mongodb-nationalparks nationalparks parksmap -n "$DEMO_NS"
oc get deploy mongodb-nationalparks nationalparks parksmap -n "$GITOPS_NS"
~~~

No data reset/seed request is required: removing the wrong hostname restores the correct existing MongoDB connection and persisted records. If GitOps sticks on a prior failed operation, investigate its revision/operation state; use the instructor recovery procedure rather than deleting namespaces, Secrets or PVCs.

## Release acceptance

- [ ] Starting state: two healthy independent National Parks stacks, completed Module 3 repair, park records present.
- [ ] Student-owned Gitea bad commit affects **only** the backend's explicit env variable.
- [ ] Live Deployment shows wrong hostname; actual Service exists under correct hostname.
- [ ] API data request fails despite backend potentially remaining Ready and GitOps potentially remaining Synced/Healthy.
- [ ] Lightspeed diagnosis is based on actual live tools, with no Secret reads.
- [ ] AgenticRun is analysis-only and functional **or** its absence is reported honestly.
- [ ] Recovery is a Gitea commit removing the override; no direct workload patches.
- [ ] Repaired data endpoint returns non-empty park records and map markers; both original and GitOps stacks are healthy.
- [ ] No shared quota/RBAC/Agentic approval/alert policy changes and no MongoDB data loss.
- [ ] Module 5 is not started with this fault still present.
