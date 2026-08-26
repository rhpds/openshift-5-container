# Module 1: What's New in OCP 5

### Brief Overview
This is an orientation module with no hands-on exercises — it is presenter-led. It sets the stage for the rest of the lab by walking attendees through the headline OpenShift 4 → 5 improvements in platform management, observability, multitenancy, and workload lifecycle. Attendees leave this module understanding why the hands-on scenarios in Modules 2-5 (GitOps onboarding, resource contention, AI-assisted troubleshooting, GitOps remediation) matter to a platform team operating a shared cluster. No student namespace interaction happens in this module; the sample application has not yet been onboarded at this point.

### Audience and Time
- **Personas:** Platform engineers / SREs responsible for onboarding and operating applications on a shared OpenShift platform (intermediate level)
- **Prerequisites for this module:** Same as the overall lab — familiarity with core OpenShift/Kubernetes concepts (pods, deployments, namespaces, RBAC) and basic Git usage. No additional module-specific prerequisites.
- **Estimated duration:** 20 minutes (presenter-led; no student action required)

### Learning Objectives
- Identify the key OpenShift 4 → 5 improvements in platform management, observability, multitenancy, and workload lifecycle that the rest of the lab will explore hands-on
- Describe how GitOps-driven onboarding, resource-contention controls, and AI-assisted troubleshooting (OpenShift Lightspeed) fit together in a modern platform engineering workflow
- Preview the shared, multi-tenant lab environment (30 concurrent students, one namespace each) and the role attendees will play as the onboarding/operating platform team in later modules

### Lab Structure
| Section | Title | Duration |
|---------|-------|----------|
| 1 | Welcome & lab scenario framing | 3 min |
| 2 | Platform management changes in OCP 5 | 4 min |
| 3 | Observability changes in OCP 5 | 4 min |
| 4 | Multitenancy changes in OCP 5 | 4 min |
| 5 | Workload lifecycle changes in OCP 5 | 3 min |
| 6 | Tour of the shared lab environment & what's ahead | 2 min |

### Detailed Steps
1. Presenter introduces the platform-team scenario: attendees will onboard, secure, and operate an application on a shared OpenShift 5 cluster over the next four modules.
2. Presenter walks through what changed in platform management between OCP 4 and OCP 5, highlighting the areas the lab will touch (cluster-level controls a platform team relies on day to day).
3. Presenter walks through observability improvements in OCP 5 — the metrics, logs, events, and traces surfaces attendees will use in Module 4 to investigate an incident.
4. Presenter walks through multitenancy improvements in OCP 5 — the namespace isolation, RBAC, and NetworkPolicy model attendees will apply and verify in Module 2.
5. Presenter walks through workload lifecycle improvements in OCP 5 — how ResourceQuotas, LimitRanges, and PriorityClasses help a platform team manage contention, previewing Module 3.
6. Presenter shows the shared lab environment layout: each student's isolated namespace on the multi-user cluster, the pre-deployed OpenShift GitOps (ArgoCD) instance, and the pre-deployed OpenShift Lightspeed assistant. Presenter notes that the sample application is not yet present — students will onboard it themselves starting in Module 2.
7. Presenter previews the arc of the remaining modules (onboard → operate under contention → investigate an AI-assisted incident → remediate through GitOps) so students know what to expect.

### Key Takeaways
- OpenShift 5 brings meaningful improvements to platform management, observability, multitenancy, and workload lifecycle over OCP 4
- The lab's hands-on modules map directly onto these four improvement areas
- OpenShift GitOps (ArgoCD) and OpenShift Lightspeed are already deployed in the environment; only the sample application remains to be onboarded
- Each student operates in an isolated namespace on a shared, multi-user cluster — the isolation itself is something they will verify hands-on in Module 2

### Infrastructure Notes
Presenter-led module — no student action or environment interaction is required. No per-student setup, validation, or access is needed for this module beyond what is already provisioned for the lab as a whole (authentication, OpenShift GitOps, and OpenShift Lightspeed, pre-deployed before the lab starts).
