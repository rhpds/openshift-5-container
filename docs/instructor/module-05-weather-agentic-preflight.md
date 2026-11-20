# Module 5 — WeatherNow GitOps Release Investigation (Instructor)

Module 5 is a 30-minute, five-mission exercise using the independent WeatherNow Application from Module 4. Its failure is an invalid container image tag, not another readiness incident. National Parks must remain untouched.

## Preflight

- Student has repaired Module 4: readinessProbe.tcpSocket.port uses named port http; image is quay.io/openshift-workshop-applications/weathernow:latest.
- Argo CD Application/weathernow-lab is Synced/Healthy in user-<guid>-gitops.
- Deployment/weathernow is 1/1 Ready, its HTTPS Route returns HTTP 200.
- Application/national-parks-settings and the three original GitOps workloads remain healthy.

Commands as instructor: oc get application weathernow-lab -n user-xxxxx-gitops; oc get deploy weathernow -n user-xxxxx-gitops; oc get route weathernow -n user-xxxxx-gitops.

## Controlled fault

Student edits only the image field in Gitea main at weathernow/weathernow.yaml, changing latest to module05-intentional-bad-tag.

Auto-Sync applies this; a new Pod should fail with ErrImagePull/ImagePullBackOff (exact event messages vary). An old ready Pod may still serve HTTP 200. Students diagnose using Lightspeed plus actual Deployment, ReplicaSet and Pod events. They must not patch live workloads, change cluster credentials, or modify Namespace/Secret/PVC/quotas.

## AgenticRun gate — deferred

See docs/instructor/agentic-student-isolation-gate.md. Student-created runs are removed from the lab steps pending a cross-namespace sandbox lifecycle fix and confirmed tenant isolation. A student may technically hold `admin` in the `-gitops` namespace; this documentation alone does not revoke that permission. The required path is Lightspeed plus namespaced rollout and event evidence. No run or approval is needed.

## Observability and release evidence

Record the image-pull Event, ReplicaSet revision, optional COO/Perses CPU/memory chart and the application log limitation while the new image cannot start. A retained old Pod may continue serving HTTP 200; this does not mean the failed release succeeded. Verify the Gitea repair commit SHA against `Application/weathernow-lab` `.status.sync.revision`, the restored image, completed rollout, and Route. Use `docs/instructor/cluster-observability-workshop-preflight.md` to validate any dashboard before relying on it.

## Recovery

Student restores the exact image to quay.io/openshift-workshop-applications/weathernow:latest through another Gitea commit, verifies Argo CD Synced/Healthy and a completed new rollout, then checks the WeatherNow HTTPS Route and the original National Parks Deployments.

## Acceptance

- [ ] Bad Gitea image commit actually reaches the live Deployment.
- [ ] New Pod pull failure is proven from events, not assumed from HTTP response.
- [ ] Student documents image-pull evidence and GitOps correction; no AgenticRun required.
- [ ] Repair Gitea commit SHA matches Argo CD source revision; latest image restored, rollout completes and Route works.
- [ ] No other student app, quota, PVC or cluster policy modified.
