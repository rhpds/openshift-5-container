# Module 4 WeatherNow screenshot capture checklist

The student captures follow the WeatherNow probe fault from the Gitea edit through automated recovery. S10 pairs the Pod event with its application log. S16 shows the two incident Pods in native OpenShift Metrics.

| Step | Published PNG | Browser evidence |
| --- | --- | --- |
| S01 | `module04-s01-weather-student-context.png` | The student GitOps project is Active in Project details |
| S02 | `module04-s02-weather-gitops-setup.png` | WeatherNow Application Sources shows the main target revision and the weathernow path |
| S03 | `module04-s03-weather-healthy-baseline.png` | WeatherNow Application details show Healthy, Synced and automatic synchronization |
| S04 | `module04-s04-weather-source.png` | WeatherNow source in Gitea with the named http readiness port |
| S05 | `module04-s05-weather-bad-probe.png` | Gitea editor with the readiness probe set to 18080 and the liveness probe still using http |
| S06 | `module04-s06-weather-fault-commit.png` | Gitea diff changing only the readiness port from http to 18080 |
| S07 | `module04-s07-weather-argocd-stalled.png` | The WeatherNow Application is Synced while rollout health is Progressing |
| S08 | `module04-s08-weather-pod-readiness.png` | WeatherNow Pods are both Running while only the previous Pod is ready |
| S09 | `module04-s09-weather-lightspeed-prompt.png` | Lightspeed prompt scoped to the WeatherNow Deployment and the unready Pod |
| S10 | `module04-s10-weather-evidence.png` | WeatherNow Pod event reports a refused readiness connection on port 18080; its application log shows port 8080 |
| S16 | `module04-s16-native-pod-readiness.png` | Native Observe Metrics shows that the old Pod became ready and the faulty Pod never did during the incident |
| S14 | `module04-s14-weather-git-repair.png` | Student Gitea repair restores the readiness probe from 18080 to http |
| S15 | `module04-s15-weather-healthy-recovered.png` | WeatherNow sync history records the automated repair and the post-repair Pods view shows one ready replica |

## Perses capture still needed

The student project showed **No dashboards found**. The guide illustrates its native **Observe → Metrics** fallback. After the tenant-authorized datasource and `PersesDashboard/workshop-workloads` pass the [observability preflight](cluster-observability-workshop-preflight.md), capture WeatherNow readiness and restart panels across the probe failure (S16).

Student-created AgenticRuns remain outside the exercise.
