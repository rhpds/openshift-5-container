# Module 5 WeatherNow screenshot capture checklist

These images are placeholders, **not screenshots of a real cluster**. Capture each screenshot from a legitimate student account (or instructor for denied access), with the correct WeatherNow baseline/fault/repaired state. Hide Gitea credentials, secrets, unrelated namespaces and private agent output.

To publish, place the matching PNG in `content/modules/ROOT/images/` and replace that one `.svg` reference with `.png` in the student page. Do not substitute a screenshot from an unrelated National Parks lab.

| Step | Placeholder SVG | Required real screenshot |
| --- | --- | --- |
| S01 | `module05-s01-weather-baseline.svg` | healthy WeatherNow image and GitOps baseline |
| S02 | `module05-s02-weather-route.svg` | working WeatherNow Route |
| S03 | `module05-s03-weather-image-source.svg` | WeatherNow image field in student Gitea |
| S04 | `module05-s04-weather-invalid-image.svg` | deliberately incorrect WeatherNow image tag and Gitea commit |
| S05 | `module05-s05-weather-imagepull-events.svg` | new WeatherNow Pod image pull failure and events |
| S06 | `module05-s06-weather-lightspeed-prompt.svg` | Lightspeed investigates WeatherNow image pull failure |
| S07 | `module05-s07-weather-registry-evidence.svg` | live image tag and pull failure events |
| S11 | `module05-s11-weather-image-repair.svg` | WeatherNow image restored in student Gitea |
| S12 | `module05-s12-weather-final-healthy.svg` | restored WeatherNow GitOps release and unaffected National Parks workloads |
| S13 | `module05-s13-perses-recovery-metrics.svg` | **REPLACE:** real student Perses dashboard for the recovery interval showing WeatherNow readiness and CPU/memory while GitOps is reconciled |

The retired S08–S10 AgenticRun images are no longer linked in Module 5; students do not execute AgenticRuns. The new S13 image is a clearly marked placeholder, **not** a live Perses screenshot. Replace it only after the tenant-authorized dashboard and actual chart data have been verified by the instructor.
