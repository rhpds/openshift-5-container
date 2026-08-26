# Module 2: GitOps Onboarding & Multitenancy

### Brief Overview
In this hands-on module, students act as the platform team onboarding a new application onto the shared OpenShift 5 cluster the GitOps way. Rather than creating resources imperatively, students declare the sample application's namespace, RBAC, and NetworkPolicy in Git and let OpenShift GitOps (ArgoCD) reconcile them. The module closes by having students verify that the multitenancy controls they just declared actually hold — that their namespace is isolated from a neighboring one.

### Audience and Time
- **Personas:** Platform engineers / SREs, intermediate level
- **Prerequisites for this module:** Module 1 orientation; basic Git usage (clone, commit, push); core OpenShift/Kubernetes concepts (namespaces, RBAC)
- **Estimated duration:** 20 minutes, hands-on

### Learning Objectives
- Configure application onboarding through GitOps (ArgoCD) by authoring and committing manifests that create the student's namespace, RBAC bindings, and NetworkPolicy
- Trigger and confirm an ArgoCD sync that reconciles the committed manifests into the live cluster state
- Verify that tenant isolation holds between the student's namespace and a neighboring namespace after onboarding (e.g., cross-namespace access is denied as expected)

### Lab Structure
| Section | Title | Duration |
|---------|-------|----------|
| 1 | Explore the GitOps repo structure | 3 min |
| 2 | Author namespace, RBAC, and NetworkPolicy manifests | 6 min |
| 3 | Commit and push, then trigger the ArgoCD sync | 4 min |
| 4 | Confirm the sample application is running | 3 min |
| 5 | Verify tenant isolation | 4 min |

### Detailed Steps
1. Open the OpenShift GitOps (ArgoCD) console/UI and locate the pre-created Application entry for the student's assigned namespace, noting that it is currently out-of-sync or missing resources.
2. Clone (or open, if pre-cloned) the student's GitOps repository and locate the directory convention used for per-user manifests.
3. Add a namespace manifest for the student's assigned namespace, including any required labels for multitenancy enforcement.
4. Add RBAC manifests (Role and RoleBinding) that grant the student the appropriate access scoped to their own namespace only.
5. Add a NetworkPolicy manifest that denies traffic from other namespaces by default while permitting the traffic the sample application needs.
6. Commit and push the manifests to the GitOps repository.
7. In the ArgoCD console/CLI, trigger (or observe the automatic) sync of the Application and watch the resources reconcile.
8. Confirm in the OpenShift console/CLI that the namespace, RBAC objects, and NetworkPolicy now exist and that the sample application workload has been onboarded successfully.
9. From within the student's namespace, attempt to reach a resource in a neighboring student's namespace (e.g., a curl to a Service in another namespace) and observe that the NetworkPolicy blocks it.
10. Attempt an RBAC-scoped action against a neighboring namespace (e.g., `oc get pods -n <other-namespace>`) and observe that it is denied, confirming tenant isolation holds.

### Key Takeaways
- GitOps-driven onboarding means namespace, RBAC, and NetworkPolicy are declared in Git and reconciled by ArgoCD, not created imperatively
- ArgoCD sync status is the source of truth for whether declared state matches live cluster state
- Declaring a NetworkPolicy and RBAC scope is not enough on its own — a platform team must verify isolation actually holds against a live neighboring tenant
- Multitenancy in OCP 5 combines namespace, RBAC, and NetworkPolicy layers; each is independently necessary

### Infrastructure Notes
Requires OpenShift GitOps (ArgoCD) pre-deployed and bootstrapped with a per-student Application/repo path before the lab starts, per the design's automation requirements. Each of the 30 concurrent students needs a distinct namespace and a neighboring student's namespace reachable (by name) for the isolation check in Step 9-10. Exact repo layout, hostnames, and sizing are TBD pending the infrastructure phase.
