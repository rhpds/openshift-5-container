# Fast-forward Modules 1 and 2 for Module 3–5 testing

This is an **instructor/lab-developer convenience**, executed from the **assigned student account**. It builds the healthy National Parks starting point directly instead of replaying the Module 1 and Module 2 console clicks. It is not a substitute for running those teaching exercises in class. It also skips intentionally broken readiness, port and GitOps discovery steps: the result is a healthy baseline, not a record of students completing every mission.

## Quick start in the student's terminal

First, use the OpenShift console's **Copy login command** to authenticate `oc` as your `user-<guid>` account. Confirm:

```bash
oc whoami
```

From any writable directory, download the script:

```bash
curl -fsSLo prepare-module03-baseline.sh \
  https://raw.githubusercontent.com/rhpds/openshift-5-container/main/automation/scripts/prepare-module03-baseline.sh
bash prepare-module03-baseline.sh
```

*While this change is in a pull request rather than `rhpds/main`, download it from the author's feature branch instead:*

```bash
curl -fsSLo prepare-module03-baseline.sh \
  https://raw.githubusercontent.com/waynedovey/openshift-5-container/feat/lab-user-fast-forward-modules-1-2/automation/scripts/prepare-module03-baseline.sh
bash prepare-module03-baseline.sh
```

The script uses the canonical public `rhpds/openshift-5-container` **main** manifests for the app. You can override `SOURCE_URL` and `SOURCE_REF` to test another trusted source revision.

If the student's Gitea repository is old, the script stops **before creating or modifying any Kubernetes application workloads** and tells you which source files differ. To explicitly restore the latest healthy Module 2 manifests in *that student's own Gitea main*, rerun:

```bash
bash prepare-module03-baseline.sh --sync-gitea
```

Git may prompt for the student's Gitea credentials or token on push. Optional noninteractive support: export `GITEA_USERNAME` and `GITEA_TOKEN` in your shell. **Never put credentials into an HTTP clone URL, commit them, or paste them into Lightspeed.** Once the Gitea change is committed, Argo CD picks it up automatically.

If the instructor recently left a **partial** manual Module 1 deployment in `-demo`, inspect the resources and only then use:

```bash
bash prepare-module03-baseline.sh --resume-demo
```

This option applies canonical resources but **does not delete** existing Secrets, PVCs or namespaces. It may conflict with immutability of a partially hand-built Deployment and will stop on errors; inspect the Deployment selectors and resource events before rerunning. It is safer to use a fresh assigned lab user than to reuse an unknown broken manual environment.

## What the script does

1. Checks that `oc whoami` returns the assigned `user-<guid>`, and that the instructor has already provisioned both `user-<guid>-demo` and `user-<guid>-gitops`. It refuses other identities, cluster-wide resource creation and namespace creation.
2. Clones the current public source manifest tree from GitHub. For GitOps, discovers **that student's** Gitea URL from the existing Gitea Route, and checks the actual student repository against canonical full-stack manifests. It preserves the harmless Module 2 ConfigMap checkpoint message.
3. For a fresh `-demo`, applies the tested namespace-scoped Module 2 manifests *without Argo CD* **in dependency order**: credentials Job and generated Secret → MongoDB 8 + PVC → Python API BuildConfig and Deployment → ParksMap discovery RBAC and frontend. It loads park data **only if the collection is empty**; the GitOps-only PostSync seed Job is not created in `-demo`.
4. If all three `-demo` Deployments already exist, it leaves them intact, apart from narrowly correcting the known Module 1 MongoDB Service targetPort `27018` to `27017` when necessary. It does not silently overwrite an incomplete, hand-built setup.
5. Creates/updates an Argo CD `Application/national-parks-settings` in `-demo` targeting the already provisioned `-gitops` namespace with Auto-Sync and Self-Heal, `prune: false`, and the ImageStream trigger `ignoreDifferences` contract from Module 2. All Module 2 resources are deployed by **Argo CD using the student's Gitea main**, not by directly applying resources to `-gitops`.
6. Confirms all three Deployments are Ready in each namespace, each API returns actual parks, the ParksMap frontend returns HTTP 200, ParksMap discovers `nationalparks`, and the GitOps Application is Synced/Healthy.

No Gitea files change unless `--sync-gitea` is explicitly provided. On refresh, only the Module 2 Kustomization/full-stack files are restored. No unrelated notes, exercise files, login credentials or secrets are altered. The command performs **no force push** and preserves the user's own harmless Module 2 message when already present.

The script **does not alter the existing shared ClusterResourceQuota**. The two application stacks and temporary build Pods still consume that quota; if quota admission fails, inspect it rather than raising the tenant limit.

The script also supports `--only-demo`, `--only-gitops`, `--insecure-tls` (only for lab routes with untrusted CA) and `--keep-workdir` for diagnostics.

## Boundaries and recovery

- The script does **not** set up the OpenShift platform, Gitea, Argo CD controller or `-gitops` namespace. Those are created by the privileged instructor tenant bootstrap.
- It cannot repair missing student edit/RBAC permissions, invalid Git credentials, a broken registry pull or an unhealthy Agentic Operator. It will stop and print contextual errors.
- It does not create AgenticRuns or configure alerting/ApprovalPolicy. Module 3 can be tested using the separate instructor-managed AgenticRun demonstration.
- It does not reset Module 4's separate backend incident if those manifests or cluster resources have been changed outside the baseline source. Use the Module 4/5 instructor recovery path if appropriate.
- Argo CD can be stuck on a **previous failed sync operation**. The script performs a hard refresh but intentionally does **not** terminate an existing operation. Inspect the Application's operation state, terminate a stale operation through the GitOps console if authorized, and rerun.
- Do not delete a MongoDB Secret/PVC to make the script pass. A PVC already containing workshop data is preserved.
- If the lab wildcard TLS certificate is not trusted by the terminal, pass `--insecure-tls` intentionally; the default verifies HTTPS.

### Expected final state

```text
MODULE 3 BASELINE READY — user-<guid>
Original:  user-<guid>-demo
GitOps:    user-<guid>-gitops
Argo CD:   user-<guid>-demo/national-parks-settings
...
You can start Module 3 without redoing the Module 1/2 UI exercises.
```

For a real preflight, also open the map in a browser and verify the park markers appear. This script's HTTP/JSON checks do not substitute for visual inspection.
