# Module 1 screenshot replacement guide

The nine PNGs in this folder are **clearly labelled placeholders**, not fake OpenShift screenshots. They are already referenced from `pages/module-01-whats-new-in-ocp5.adoc`.

## How to replace them

1. Log into the **actual OpenShift 5 workshop cluster as a student** (not as cluster-admin). Select your assigned National Parks project.
2. Capture the real screen described below. Use roughly 16:9 framing, ideally 1440×810 or a wider console capture cropped to the relevant task. Keep enough navigation/breadcrumb visible to show where the learner clicked.
3. Add at most 1–3 readable numbered callouts. Never include passwords, access tokens, kubeconfigs, unrelated customer data, or Secret values.
4. Save the screenshot as a **PNG with exactly the same filename** listed below.
5. In GitHub, open this folder, choose **Add file → Upload files**, upload the corresponding file with the existing name, and commit the replacement to your working branch. You can also replace the file via Git and push. Do not delete/rename it or edit the AsciiDoc image reference.
6. Review the rendered student module. The new image replaces the placeholder automatically because the filename and path stay unchanged.

## Capture specification

| ID | Filename | Capture the genuine student view | Callouts / checks |
|---|---|---|---|
| S00 | `module01-s00-console.png` | New OpenShift 5 console landing view using the Project Felt theme, with the student's project selected | Updated appearance, project selector, navigation; no credentials |
| S01 | `module01-s01-map.png` | National Parks map with loaded park markers and one marker selected | Application is functional, populated dataset |
| S02 | `module01-s02-topology.png` | `Workloads → Topology` for assigned project | Project selector; `parksmap`; `nationalparks`; `mongodb-nationalparks` |
| S03 | `module01-s03-route.png` | `Networking → Routes → parksmap` | Hostname, TLS, Service target and admission when visible; instructor separately verifies serving controller's effective HAProxy version |
| S04 | `module01-s04-service.png` | `Networking → Services → parksmap`; optionally matching pod view | Selector, port and matching ready frontend pod |
| S05 | `module01-s05-scale-before.png` | Frontend Deployment/Topology scaling control before change | 1 desired/1 ready; **exact UI action** used to scale |
| S06 | `module01-s06-scale-after.png` | Frontend after scale | 2 desired/2 ready; two pods; optional ready endpoints inset |
| S07 | `module01-s07-lightspeed.png` | Lightspeed chat with student-scoped request and **real tool evidence** | Actual namespace, successful tool result and matching data; redact secrets |
| S08 | `module01-s08-health.png` | Workload health/logs after restoring baseline | Healthy components, relevant logs/events, 1/1 frontend after reset |

## Before publication

- [ ] Every placeholder PNG has been replaced with a **real** OpenShift 5 capture.
- [ ] Navigation labels in student instructions match the same cluster build and identity shown in screenshots.
- [ ] S05–S06 reflect a scale operation the student can actually perform with scoped RBAC, without fighting HPA/GitOps reconciliation.
- [ ] S07 shows tool evidence, not merely an assistant claiming it called tools. When no live result can be captured, revise the student checkpoint instead of fabricating one.
- [ ] S00 is from the OpenShift 5 console and visibly demonstrates the revised UI rather than a historical 4.x screenshot.
- [ ] All screenshots have legible labels, no credentials/Secrets, and a consistent visual style.
- [ ] A rehearsal with two student identities completes all steps in 25 minutes.

## Antora path

These assets live under `content/modules/ROOT/images/` and are referenced as `image::module01-sXX-....png[...]` from the student AsciiDoc. There is no manual step to uncomment an image, alter a path or configure an image host after you replace a placeholder file.
