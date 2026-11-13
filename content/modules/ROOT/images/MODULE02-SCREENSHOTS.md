# Module 2 screenshot checklist — full-stack Auto-Sync

Module 2 now teaches the **entire National Parks application** through the
**GA OpenShift GitOps console plug-in**. Capture actual evidence for the new
45-minute, Auto-Sync workflow. All twelve SVG placeholders still render; they
are **SCREENSHOT NEEDED** markers, not cluster evidence.

Students are never instructed to upload or edit screenshots.

## Screenshot inventory

| ID | Mission | Final PNG name | Required real-world evidence |
|---|---|---|---|
| S01 | 1 | `module02-s01-student-context.png` | Student oc whoami, cluster version, both -demo/-gitops namespaces; never show password |
| S02 | 1 | `module02-s02-lightspeed-mcp-inspection.png` | Lightspeed real read-only tool output for namespace/application inspection |
| S03 | 2 | `module02-s03-gitea-source.png` | Student Gitea root kustomization.yaml lists fullstack and the complete fullstack/ tree |
| S04 | 3 | `module02-s04-argocd-new-app.png` | Native GitOps console Application YAML, Auto-Sync/Self-Heal on, prune off, source root |
| S05 | 3 | `module02-s05-argocd-initial-outofsync.png` | GitOps plug-in resource tree during initial full-stack reconciliation |
| S06 | 4 | `module02-s06-argocd-initial-synced.png` | Full-stack GitOps resources including all three Deployments |
| S07 | 4 | `module02-s07-ocp-gitops-console.png` | Python backend Build complete, ImageStreamTag nationalparks:latest present |
| S08 | 4 | `module02-s08-gitea-commit.png` | MongoDB PVC Bound, healthy deployment and credentials bootstrap evidence without Secret data |
| S09 | 4 | `module02-s09-argocd-drift.png` | ParksMap and Python HTTPS Routes plus loaded park data |
| S10 | 5 | `module02-s10-lightspeed-drift.png` | Gitea edit/commit to fullstack/national-parks-gitops-info.yaml |
| S11 | 5 | `module02-s11-argocd-resynced.png` | Automatic reconciliation and updated ConfigMap message; no manual Sync |
| S12 | 5 | `module02-s12-tenant-rbac.png` | Student RBAC and independent live Deployments in -demo and -gitops |

**These filenames are retained for compatibility with the existing SVG
placeholders. Their old manual-sync meanings no longer apply.**

## Capture and publication process

1. Rehearse with a real disposable student identity and actual Gitea
   repository (not a public GitHub URL or instructor-admin identity).
2. Capture at least 1440 px width when possible. Show relevant OpenShift
   navigation, namespace and resource names.
3. Redact passwords, bearer tokens, Secret values, private data and
   unrelated tenants. Never show an oc login -p command with the password.
4. Save images under content/modules/ROOT/images with the exact names
   above. After a PNG is committed, replace only the corresponding
   image::module02-....svg[] reference in the AsciiDoc page.
5. Leave other .svg placeholders until genuine images are available;
   never switch an image path to an uncommitted file.
6. Inspect the rendered Antora/Showroom page after each capture batch.
7. Record elapsed build and PVC provisioning time before saying the
   full-stack student lab fits 45 minutes.

## Evidence quality

* S04 must show the Application CR in student -demo and destination
  namespace -gitops. Automated sync enabled, selfHeal true, prune false,
  RespectIgnoreDifferences=true.
* S03 must show the **root** Kustomization with resources: - fullstack.
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

- [ ] All 12 references resolve to genuine PNGs or labelled SVG placeholders
- [ ] Main module shows the full-stack Auto-Sync journey, not the retired manual-sync exercise
- [ ] Two real student end-to-end rehearsals complete successfully
- [ ] Gitea full-stack source and root Kustomization are present in the actual student repository
- [ ] Build/Images/Storage/Routes/Jobs/data and 3 Deployments are validated
- [ ] All images conceal credentials and unrelated tenants
- [ ] Students do not upload screenshots
