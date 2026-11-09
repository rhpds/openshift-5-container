# Module 1: native-console deployment screenshot guide

The 25-minute Mission National Parks now starts with **an empty application
namespace**. Screenshots S01–S08 must be recaptured to match the **new deployment
journey**; the older PNG placeholder illustrations may still describe the prior
scale-first exercise. They are placeholders, **not screenshots of a tested lab**.

S00 was previously uploaded from the OpenShift 5 Projects view, but it shows
`user-pjbsb-demo`. Before final publication, capture the *actual application*
namespace (`user-pjbsb` in that example) with the student identity and make
sure the project is accessible. The `-demo` namespace can be used for Argo CD
or other workshop services and is not necessarily where the app belongs.

## Capture list (use the exact filenames)

| ID | Filename | New screen to capture | Evidence or callout |
|---|---|---|---|
| S00 | `module01-s00-console.png` | Student sees their application project in the OCP 5 Projects list | Project Felt appearance and correct namespace; **recapture** |
| S01 | `module01-s01-map.png` | Populated National Parks map after the student loads data | Visible park markers and one selected park |
| S02 | `module01-s02-topology.png` | Topology showing all three newly created workloads | `parksmap`, `nationalparks`, `mongodb-nationalparks` |
| S03 | `module01-s03-route.png` | `Networking → Routes → nationalparks` | Route hostname and `type=parksmap-backend` label |
| S04 | `module01-s04-service.png` | `Networking → Services → mongodb-nationalparks` | Internal ClusterIP; no database Route |
| S05 | `module01-s05-scale-before.png` | **Now repurposed:** Quick create → Container images, before `parksmap` creation | Correct image, application/name, Deployment, Create route |
| S06 | `module01-s06-scale-after.png` | **Now repurposed:** Import from Git (or its Build progress), creating `nationalparks` | Git source, Python builder, name and status |
| S07 | `module01-s07-lightspeed.png` | Lightspeed response showing real MCP tool results for the newly deployed app | Successful read evidence and matching workload/Route state |
| S08 | `module01-s08-health.png` | Final health in OCP 5 console | Three ready workloads, two Routes, working map |

The filenames for S05 and S06 intentionally remain unchanged in this commit so
that the existing Antora asset references remain valid while screenshots are
recollected. When the new PNGs arrive we can give them better deployment-themed
filenames and update the two image references together.

## How to replace a screenshot

1. Log into the actual OCP 5 workshop cluster as a **student**, not as admin.
2. Capture at approximately 16:9 (ideally 1440 × 810) with sufficient console
   navigation visible for a student to reproduce the click path.
3. Use one or two small numbered callouts at most. Do not include Secret
   values, bearer tokens, passwords, kubeconfigs or unrelated customer data.
4. Save the PNG using the *exact* filename above and replace it in
   `content/modules/ROOT/images/` on your fork.
5. Check the rendered Module 1 on your fork's GitHub Pages preview before
   submitting an upstream PR.

## Acceptance before delivery

- [ ] S00 shows the student's application namespace rather than just `-demo`.
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
