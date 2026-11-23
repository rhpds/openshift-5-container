# Module 5 WeatherNow screenshot capture checklist

The student captures follow one WeatherNow image change through the registry failure and Git repair. S06 shows the investigation prompt. S07 supplies the registry’s actual error. S13 shows the native OpenShift memory series after recovery.

| Step | Published PNG | Browser evidence |
| --- | --- | --- |
| S01 | `module05-s01-weather-baseline.png` | The baseline WeatherNow Pod is Running and ready before the image change |
| S02 | `module05-s02-weather-route.png` | The WeatherNow route returns a forecast in the browser |
| S03 | `module05-s03-weather-image-source.png` | The WeatherNow Deployment source in Gitea uses the working latest image tag |
| S04 | `module05-s04-weather-invalid-image.png` | Gitea diff replaces the working WeatherNow tag with module05-intentional-bad-tag |
| S05 | `module05-s05-weather-imagepull-events.png` | The new WeatherNow Pod reports ImagePullBackOff while the previous Pod remains ready |
| S06 | `module05-s06-weather-lightspeed-prompt.png` | Read-only Lightspeed prompt for the failed image naming the Deployment, ReplicaSet, Pod and Pod UID |
| S07 | `module05-s07-weather-registry-evidence.png` | The Pod event names the bad tag and reports manifest unknown from the image registry |
| S11 | `module05-s11-weather-image-repair.png` | Student Gitea repair restores the working WeatherNow image tag |
| S12 | `module05-s12-weather-final-healthy.png` | Both WeatherNow and National Parks are Synced and Healthy at the repair revision |
| S13 | `module05-s13-native-recovery-memory.png` | Native Observe Metrics shows the serving WeatherNow Pod’s memory working set in MiB after recovery |

## Perses capture still needed

The student project showed **No dashboards found**. The guide illustrates its native **Observe → Metrics** fallback. After the tenant-authorized datasource and `PersesDashboard/workshop-workloads` pass the [observability preflight](cluster-observability-workshop-preflight.md), capture WeatherNow readiness and CPU or memory panels across the image repair (S13).

Student-created AgenticRuns remain outside the exercise.
