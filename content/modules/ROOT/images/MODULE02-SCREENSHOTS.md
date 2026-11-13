# Module 2 screenshot capture checklist

Module 2 has **12 renderable SVG screenshot placeholders**, displayed in the student guide and clearly marked **SCREENSHOT NEEDED**. These are *not* live screenshots. **Students do not need to capture or upload anything.** The instructor adds genuine OpenShift 5 **GA GitOps console plug-in**, Gitea and Lightspeed images. Standalone Argo CD is fallback evidence for the manual Sync action only.

## Screenshot inventory

| ID | Location | Final PNG name | Evidence required |
|---|---|---|---|
| S01 | Mission 1 | `module02-s01-student-context.png` | Terminal: whoami, project, version; no login password |
| S02 | Mission 1 | `module02-s02-lightspeed-mcp-inspection.png` | Real Lightspeed tool, namespace and result |
| S03 | Mission 2 | `module02-s03-gitea-source.png` | Student Gitea path and two GitOps source files |
| S04 | Mission 3 | `module02-s04-argocd-new-app.png` | OpenShift GitOps -> Applications -> Create Application YAML, metadata namespace -demo, destination -gitops, no automated sync |
| S05 | Mission 3 | `module02-s05-argocd-initial-outofsync.png` | Native GitOps console Application Details/Resources: only the ConfigMap missing before first sync |
| S06 | Mission 3 | `module02-s06-argocd-initial-synced.png` | Native GitOps console: Synced/Healthy, one managed ConfigMap |
| S07 | Mission 3 (required) | `module02-s07-ocp-gitops-console.png` | GA GitOps navigation: Applications, ApplicationSets and AppProjects |
| S08 | Mission 4 | `module02-s08-gitea-commit.png` | Commit with Updated in Gitea; no credentials |
| S09 | Mission 4 | `module02-s09-argocd-drift.png` | Native GitOps console: OutOfSync after Git commit, before resync |
| S10 | Mission 4 | `module02-s10-lightspeed-drift.png` | MCP evidence explains manual sync and old message |
| S11 | Mission 4 | `module02-s11-argocd-resynced.png` | Native GitOps console: Synced/Healthy, latest ConfigMap |
| S12 | Mission 5 | `module02-s12-tenant-rbac.png` | Student vs openshift-config access result |

**S07 is required:** the GA GitOps console plug-in is the primary Module 2 interface. If it is unavailable, the workshop preflight is incomplete. Do not fabricate a screenshot or silently substitute the standalone Argo CD interface. Leave the SVG placeholder until a genuine console capture is available.

## How to replace each placeholder

1. Capture the **actual** student lab screen as instructor, ideally at least 1440 px wide and with useful navigation chrome in frame.
2. Redact passwords, bearer tokens, kubeconfigs, Secret values, personal data and unrelated customer namespaces. For S01 capture `oc whoami`, `oc project` and `oc version` output **after login**, never the password-bearing `oc login -p` command.
3. Put the file in `content/modules/ROOT/images/` using the exact **PNG name** above.
4. After the PNG is committed, replace its single `image::module02-....svg[]` reference in `content/modules/ROOT/pages/module-02-gitops-onboarding-multitenancy.adoc` with the identical `.png` filename. Do **not** switch references before the image exists, or the published page will show a broken image.
5. Keep the other SVG placeholders until their corresponding PNGs arrive; images can be replaced incrementally. Verify the rendered Showroom page after each batch.

## Capture details

- S02 and S10: Expand Lightspeed's *actual read-only MCP tool call*, showing namespace, tool name and returned resource data. Do not use AI text alone as proof of cluster state.
- S04/S05/S06/S07/S09/S11: Capture the native OpenShift **GitOps** navigation and Application Details/Resources tabs. S05 and S09 show **OutOfSync** and one-ConfigMap diff; S06 and S11 show **Synced/Healthy** after manual sync. The S04 creation screenshot must show the Application in the Argo CD control-plane namespace (-demo), not the -gitops destination project.
- S03/S08: Show the Git source path and the actual student Gitea commit; exclude login credentials.
- S12: Show the actual `oc auth can-i` results. If tenant RBAC differs, revise expectations; never manufacture a `no` result.
- S07: Required GitOps console plug-in navigation. Confirm the plug-in is enabled **before class**. Do not install it during the student exercise.
- Existing Module 1 working map screenshots can be reused for the final functional check; no duplicate map capture is required.

## Acceptance

- [ ] All delivered screenshots are actual captures, not placeholder artwork
- [ ] S01, S02, S03 are from a correctly authenticated student namespace
- [ ] S04-S07 document the native GA GitOps console Application creation, resource inspection and initial manual sync
- [ ] S08-S11 document a Gitea commit, GitOps console drift, read-only Lightspeed diagnosis and second manual sync
- [ ] S12 illustrates the actual student RBAC boundary
- [ ] No uploaded image contains credentials or tokens
- [ ] Every image reference in the rendered Antora page resolves to a committed PNG or SVG
- [ ] Students are never instructed to upload workshop screenshots
