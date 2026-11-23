# Module 1 screenshot guide

The [student walkthrough](../pages/module-01-whats-new-in-ocp5.adoc) places each screenshot beside the action or result it illustrates. All were captured from the same student seat on 23 November 2026. The example project is `user-cg6vc-demo`. Each participant selects their own demo project.

| Mission | What to look for in the captures |
|---|---|
| 0 · Select the project | Home → Projects lists the demo and GitOps projects. The account control shows the console identity. Students verify their terminal identity separately with `oc whoami`. |
| 1 · Deploy ParksMap | The external image validates, the frontend uses port 8080, and four labels are committed. The Resources panel shows the Pod, Service and Route. The YAML import creates the three dedicated discovery objects. The first map has no markers. |
| 2 · Build the API | The Git form recommends Dockerfile. The existing application group contains a component named `nationalparks`. The fifth label, `type=parksmap-backend`, appears on the Service. The build log ends in a successful push. The root Route returns the welcome message. |
| 3 · Wire MongoDB | The Secret form shows the first, non-password entry. The import shows the deliberate target port. Three console excerpts show the ConfigMap, Deployment and Service. The Python Deployment's Environment tab shows the saved Secret reference. The data Route returns HTTP 504 in this run. |
| 4 · Diagnose | The Lightspeed mode selector shows Troubleshooting. The answer includes two resource reads and explains the difference between the Service target port and MongoDB's container port. |
| 5 · Approve and verify | The live Service details show 27017 → 27018 before the repair. The review card and action details show the proposed numeric target port and the approval controls. The chat reports a network error. The saved Service shows 27017 → 27017 after approval. The one-time load reports 2,893 insertions. |
| 6 · Verify the result | The public API terminal checks return the record count and backend identity. The map displays the National Parks (PY) layer and clustered markers. The filtered Topology list shows one Pod for each of the three workloads. |

Keep credential values out of captures. When refreshing these figures, check trigger and result separately, especially the tool approval and the saved Service. A screenshot of a command alone cannot establish that it ran.
