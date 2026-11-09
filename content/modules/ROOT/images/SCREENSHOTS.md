# Module 1: native-console deployment screenshot guide

The 25-minute Mission National Parks uses the student's **existing** workshop
project, `user-%GUID%-demo` (the Antora text displays this as `{lab_user}-demo`).
Students do **not** create a new namespace. In the supplied console captures,
the project is `user-pjbsb-demo`, which matches this design.

The real OpenShift 5 screenshots for the *Create from Container Image* journey
are now uploaded as S05a–S05e. S00 is also a real Projects screen. Screenshots
S01–S04 and S06–S08 still need to be recaptured after deployment; the old PNGs
in those slots are illustrations, **not proof of a working lab**.

## Capture list (use the exact filenames)

| ID | Filename | New screen to capture | Evidence or callout |
|---|---|---|---|
| S00 | `module01-s00-console.png` | Student sees `user-<GUID>-demo` in the Projects list | Existing project; no *Create Project* action |
| S01 | `module01-s01-map.png` | Populated National Parks map after the student loads data | Visible park markers and one selected park |
| S02 | `module01-s02-topology.png` | Topology showing all three newly created workloads | `parksmap`, `nationalparks`, `mongodb-nationalparks` |
| S03 | `module01-s03-route.png` | `Networking → Routes → nationalparks` | Route hostname and `type=parksmap-backend` label |
| S04 | `module01-s04-service.png` | `Networking → Services → mongodb-nationalparks` | Internal ClusterIP; no database Route |
| S05a | `module01-s05a-container-images-menu.png` | OpenShift 5 top-bar `+` menu | Choose *Container images*; **uploaded** |
| S05b | `module01-s05b-image-and-project.png` | Deploy Image form | Validated `quay.io/openshiftroadshow/parksmap:latest` and `user-<GUID>-demo`; **uploaded** |
| S05c | `module01-s05c-runtime-and-app.png` | Runtime icon and General settings | Default `openshift` icon, Create application, `national-parks-app`, `parksmap`; **uploaded** |
| S05d | `module01-s05d-deployment-and-route.png` | Deploy and Advanced options | Deployment, target port `8080`, Create a route checked; **uploaded** |
| S05e | `module01-s05e-frontend-labels.png` | Frontend labels | Four exact workload labels; **uploaded** |
| S06 | `module01-s06-scale-after.png` | **Now repurposed:** Import from Git (or its Build progress), creating `nationalparks` | Git source, Python builder, name and status |
| S07 | `module01-s07-lightspeed.png` | Lightspeed response showing real MCP tool results for the newly deployed app | Successful read evidence and matching workload/Route state |
| S08 | `module01-s08-health.png` | Final health in OCP 5 console | Three ready workloads, two Routes, working map |

The previous `module01-s05-scale-before.png` image is retired from Module 1;
S05a–S05e replace that placeholder. The old S06 filename remains until we
receive a matching screenshot of the Python import/build.

## How to replace a screenshot

1. Log into the actual OCP 5 workshop cluster as a **student**, not as admin.
   Select the already-provisioned `user-<GUID>-demo` project. Do not create a
   duplicate namespace or select a different student's project.
2. Capture at approximately 16:9 (ideally 1440 × 810) with sufficient console
   navigation visible for a student to reproduce the click path.
3. Use one or two small numbered callouts at most. Do not include Secret
   values, bearer tokens, passwords, kubeconfigs or unrelated customer data.
4. Save the PNG using the *exact* filename above and replace it in
   `content/modules/ROOT/images/` on your fork.
5. Check the rendered Module 1 on your fork's GitHub Pages preview before
   submitting an upstream PR.

## Acceptance before delivery

- [x] S00 shows the student's pre-existing `user-<GUID>-demo` project.
- [x] S05a–S05e show the Console navigation, validated frontend image, project,
      runtime, application name, Deployment, Route and labels.
- [ ] Student can deploy into `user-<GUID>-demo` without modifying the existing
      Argo CD, Gitea or Showroom components in that namespace.
- [ ] The student can create frontend/BuildConfig/Route resources through the
      actual OCP 5 console and see the newly created Topology group.
- [ ] The backend source build and MongoDB image pull were both tested under
      student-level permissions and complete within the allotted time.
- [ ] The Secret reference, backend Route discovery label, data load and map
      marker display all work as documented.
- [ ] Screenshots are authentic, legible and match the current Project Felt UI.
- [ ] MCP screenshot captures successful tool-result evidence, not just an AI
      claim. If no tool calls are available, change the lab result accordingly.
- [ ] Two students independently finish in 25 minutes or the timing is revised.
