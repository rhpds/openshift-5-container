# Module 4 WeatherNow screenshot capture checklist

These images are placeholders, **not screenshots of a real cluster**. Capture each screenshot from a legitimate student account (or instructor for denied access), with the correct WeatherNow baseline/fault/repaired state. Hide Gitea credentials, secrets, unrelated namespaces and private agent output.

To publish, place the matching PNG in `content/modules/ROOT/images/` and replace that one `.svg` reference with `.png` in the student page. Do not substitute a screenshot from an unrelated National Parks lab.

| Step | Placeholder SVG | Required real screenshot |
| --- | --- | --- |
| S01 | `module04-s01-weather-student-context.svg` | pre-existing student gitops namespace |
| S02 | `module04-s02-weather-gitops-setup.svg` | student Gitea WeatherNow source and new Application |
| S03 | `module04-s03-weather-healthy-baseline.svg` | healthy WeatherNow GitOps Application and Route |
| S04 | `module04-s04-weather-source.svg` | Gitea WeatherNow Deployment source |
| S05 | `module04-s05-weather-bad-probe.svg` | WeatherNow incorrect probe port in Gitea editor |
| S06 | `module04-s06-weather-fault-commit.svg` | student Gitea fault commit |
| S07 | `module04-s07-weather-argocd-stalled.svg` | GitOps sees new source but WeatherNow rollout is stalled |
| S08 | `module04-s08-weather-pod-readiness.svg` | old and new WeatherNow Pods and readiness failure |
| S09 | `module04-s09-weather-lightspeed-prompt.svg` | Lightspeed WeatherNow investigation prompt |
| S10 | `module04-s10-weather-evidence.svg` | live probe, ReplicaSet, Events plus supporting metrics/log observation; do not imply metrics are shown if absent |
| S16 | `module04-s16-perses-weather-readiness.svg` | **REPLACE:** student project, named Perses workload dashboard, incident time range with WeatherNow Ready Pods, restarts, CPU/memory; do not mistake missing data for zero |
| S14 | `module04-s14-weather-git-repair.svg` | WeatherNow repaired source and Git commit |
| S15 | `module04-s15-weather-healthy-recovered.svg` | WeatherNow and GitOps healthy after repair |

The new S16 screenshot placeholder is linked in Mission 3 and must be replaced with genuine student evidence before publication. The retired S11–S13 AgenticRun placeholders are no longer linked from the student guide. Do not show or capture a student-created AgenticRun until the operator cross-namespace lifecycle and tenant-isolation defects have been resolved and re-enabled in a separately reviewed change. An optional sanitized instructor example is not an assessment requirement.
