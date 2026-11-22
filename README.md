# LB1858 · Operating Applications on OpenShift 5

This repository supplies the Showroom guide and GitOps bootstrap charts for the per-student lab. Provision the shared `lb1858-ocp5-container-mngmt-cluster` catalog item and confirm it is running before ordering student seats.

| Module | Student outcome |
| --- | --- |
| 1. National Parks | Deploy a three-tier application, diagnose its MongoDB Service, and verify the data and map. |
| 2. GitOps and multitenancy | Deploy from student Gitea through Argo CD. Grant and revoke one named read, and prove ingress isolation against an independent reference tenant. |
| 3. Workload management | Measure ParksMap, test quota admission with server-side dry runs and verify a sizing decision. |
| 4. Incident investigation | Correlate the new WeatherNow pod's readiness event, application logs and metrics with the faulty Git revision. |
| 5. Application lifecycle | Diagnose an image-pull failure, repair the source in Gitea and verify the reconciled revision and available replicas. |

[Student guide](https://rhpds.github.io/openshift-5-container/) · [Instructor preparation](docs/instructor/README.md)

The shared chart provisions the reference tenant. The per-seat chart provisions its independent test client and the student's Argo CD and Gitea. Student GitOps manifests and setup scripts are maintained in the [workspace repository](https://github.com/rhpds/openshift-5-container-workspace). Each student edits an imported Gitea copy.

## Validate changes

Run the curriculum tests from this checkout. Set `WORKSPACE_REPO_DIR` to a local workspace checkout for offline testing. The Pages workflow builds the guide with Antora using the vendored Showroom theme.

```sh
python3 -m unittest discover -s tests
helm lint automation/gitops/bootstrap-infra
helm lint automation/gitops/bootstrap-tenant
```

For a workshop release, rehearse in a provisioned student seat with the matching Showroom and bootstrap revisions. The student evidence tables specify what to capture in the live cluster.
