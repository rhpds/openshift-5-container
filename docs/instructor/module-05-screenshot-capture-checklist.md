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
| S08 | `module05-s08-weather-agentic-permission.svg` | WeatherNow AgenticRun permission gate |
| S09 | `module05-s09-weather-agentic-create.svg` | permitted student-created WeatherNow analysis-only run |
| S10 | `module05-s10-weather-agentic-evidence.svg` | WeatherNow run analysis evidence or instructor fallback |
| S11 | `module05-s11-weather-image-repair.svg` | WeatherNow image restored in student Gitea |
| S12 | `module05-s12-weather-final-healthy.svg` | restored WeatherNow GitOps release and unaffected National Parks workloads |

Only show a student-created AgenticRun after the instructor isolation gate has passed; otherwise capture the permission-denied outcome and documented instructor fallback. The static placeholder must never imply that an AgenticRun completed successfully.
