# Module 2 screenshot checklist — full-stack Auto-Sync

The twelve PNGs follow a student from project selection through a full-stack Auto-Sync deployment and the reference-tenant isolation exercise. The final image combines five timestamped samples from the same reference client and Service.

Students are never instructed to upload or edit screenshots.

## Screenshot inventory

| ID | Mission | Final PNG name | Published browser view |
|---|---|---|---|
| S01 | 1 | `module02-s01-student-context.png` | The student’s two active projects in the OpenShift console |
| S02 | 1 | `module02-s02-lightspeed-mcp-inspection.png` | Read-only Lightspeed inventory prompt and its one-ready-of-one MongoDB result in the GitOps project |
| S03 | 2 | `module02-s03-gitea-source.png` | The national-parks Kustomization and its resource list in student Gitea |
| S04 | 3 | `module02-s04-argocd-new-app.png` | Create Argo CD Application with the student Gitea source, destination and automated sync policy |
| S05 | 3 | `module02-s05-argocd-initial-outofsync.png` | National Parks Application details during the first sync show OutOfSync and Progressing |
| S06 | 4 | `module02-s06-argocd-initial-synced.png` | MongoDB, the National Parks backend and ParksMap each have one of one Pods in the GitOps project |
| S07 | 4 | `module02-s07-ocp-gitops-console.png` | The nationalparks backend Build completed in the GitOps project |
| S08 | 4 | `module02-s08-gitea-commit.png` | The mongodb-nationalparks-data persistent volume claim is Bound with 1 GiB capacity |
| S09 | 4 | `module02-s09-argocd-drift.png` | The GitOps ParksMap route displays park markers and clusters on the map |
| S10 | 5 | `module02-s10-lightspeed-drift.png` | Student Gitea commit changing the message in national-parks-gitops-info.yaml |
| S11 | 5 | `module02-s11-argocd-resynced.png` | The reconciled ConfigMap contains the message Updated through GitOps Auto-Sync |
| S12 | 5 | `module02-s12-tenant-rbac.png` | Reference client log excerpts from baseline, read grant, ingress isolation, read revocation and restored connectivity |

**A screenshot showing only `national-parks-gitops-info`, even with *Healthy*
and *Synced* badges, is evidence of the stale legacy exercise and must NOT
replace S05 or S06.**

The original S01–S12 identifiers are retained for instructor reference.

## Capture and publication process

1. Rehearse with a real disposable student identity and actual Gitea
   repository (not a public GitHub URL or instructor-admin identity).
2. Capture at least 1440 px width when possible. Show relevant OpenShift
   navigation, namespace and resource names.
3. Redact passwords, bearer tokens, Secret values, private data and
   unrelated tenants. Never show an oc login -p command with the password.
4. Save each PNG under `content/modules/ROOT/images/` using the filename above.
5. Inspect the rendered Antora/Showroom page and confirm every image matches its caption.
6. Record elapsed build and PVC provisioning time before saying the
   full-stack GitOps segment fits 45 minutes, plus a 20-minute tenant-isolation checkpoint.

## Evidence quality

* S04 must show both the Argo CD Application CR and its destination in student -gitops, not -demo. Automated sync enabled, selfHeal true, prune false,
  RespectIgnoreDifferences=true.
* S03 must show national-parks/kustomization.yaml with all seven manifests.
  The older single-ConfigMap root is no longer acceptable evidence.
* S06–S09 must show three Deployments, three Services, two Routes,
  a completed Python build, PVC Bound, and real park data. A successful
  healthz check alone is not proof of loaded records.
* S10–S11 must demonstrate **a Gitea commit followed by Auto-Sync**.
  Do not show students clicking Sync or performing manual cluster patches.
* S02 / S11 Lightspeed claims need real tool evidence. A model narrative
  without successful resource reads does not establish cluster health.
* S12 must show real RBAC answers, never manufactured yes/no results.
* No screenshot may display MongoDB credentials, Secret values or tokens.

## Acceptance

- [ ] All 12 references resolve to the genuine PNGs listed above
- [ ] Main module shows the full-stack Auto-Sync journey, not the retired manual-sync exercise
- [ ] Two real student end-to-end rehearsals complete successfully
- [ ] Gitea full-stack source and root Kustomization are present in the actual student repository
- [ ] Build/Images/Storage/Routes/Jobs/data and 3 Deployments are validated
- [ ] All images conceal credentials and unrelated tenants
- [ ] Students do not upload screenshots

## New tenant isolation evidence

Capture the local HTTP control, the reference tenant's 403 → 200 → 403 API responses, its HTTP 200 → connect timeout → 200 network results, and cleanup. Capture the optional second enrolled student's results separately when exercised.
