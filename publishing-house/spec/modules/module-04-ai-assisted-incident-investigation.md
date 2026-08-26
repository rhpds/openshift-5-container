# Module 4: AI-Assisted Incident Investigation

### Brief Overview
This is the centerpiece hands-on module of the lab. An injected fault degrades the sample application in the student's namespace, and students use OpenShift Lightspeed alongside traditional observability signals — metrics, logs, events, and traces — to investigate the incident. Crucially, students don't just accept Lightspeed's suggestions: they validate them against real cluster data before deciding on a fix, which they'll implement in Module 5.

### Audience and Time
- **Personas:** Platform engineers / SREs, intermediate level
- **Prerequisites for this module:** Modules 2-3 completed (application onboarded, resource controls in place); general troubleshooting instincts; basic familiarity with metrics/logs/traces concepts
- **Estimated duration:** 40 minutes, hands-on

### Learning Objectives
- Troubleshoot an injected production incident using OpenShift Lightspeed together with metrics, logs, and traces
- Formulate investigation questions and interpret OpenShift Lightspeed's conversational guidance in the context of the observed incident
- Verify OpenShift Lightspeed's recommendations against real cluster data (metrics, logs, events, traces) before acting on them
- Converge on a validated root cause and a candidate fix to carry into Module 5's GitOps remediation

### Lab Structure
| Section | Title | Duration |
|---------|-------|----------|
| 1 | Discover the incident | 5 min |
| 2 | Engage OpenShift Lightspeed for initial guidance | 8 min |
| 3 | Examine metrics and dashboards | 6 min |
| 4 | Examine logs and events | 7 min |
| 5 | Examine traces | 6 min |
| 6 | Cross-validate Lightspeed's hypothesis and converge on a fix | 8 min |

### Detailed Steps
1. Observe the sample application exhibiting degraded behavior in the student's namespace (e.g., failing health checks, elevated error rate, or unavailable endpoint) as a result of the injected fault.
2. Open OpenShift Lightspeed and describe the symptom in natural language, asking it to help diagnose the issue.
3. Read Lightspeed's initial response, noting the hypothesis or hypotheses it proposes and any cluster objects it references.
4. Navigate to the OpenShift console's metrics/dashboards for the affected workload and check whether the metrics support or contradict Lightspeed's hypothesis (e.g., CPU/memory saturation, restart counts, request latency).
5. Query pod logs for the affected workload and look for error messages or stack traces consistent with (or inconsistent with) Lightspeed's hypothesis.
6. Review relevant Kubernetes events for the namespace/workload (e.g., `oc get events`) for scheduling, probe, or image-pull signals that corroborate or refute the hypothesis.
7. Inspect distributed traces for the affected request path to pinpoint where latency or failure is introduced.
8. Return to OpenShift Lightspeed with the additional evidence gathered and ask follow-up questions to refine or challenge its original hypothesis.
9. Explicitly compare Lightspeed's final recommendation against the metrics/logs/events/traces evidence collected, and decide whether to accept, adjust, or reject the recommendation.
10. Document (or note for the next module) the validated root cause and the specific fix to be applied — this hands off directly into Module 5.

### Key Takeaways
- OpenShift Lightspeed accelerates investigation but its output is a hypothesis, not a verdict
- Metrics, logs, events, and traces each surface a different facet of an incident; a full picture usually requires combining more than one
- Validating an AI recommendation against real cluster data before acting is a core platform-engineering discipline, not an optional step
- A well-scoped incident investigation converges on a specific, testable fix rather than a vague conclusion

### Infrastructure Notes
Requires OpenShift Lightspeed pre-deployed (via the existing `agnosticd.ai_workloads.ocp4_workload_ols` role, per design — an external, Azure-managed service rather than a lab-deployed model) and a pre-built sample application workload with an injectable fault, per the design's automation requirements. The fault must be reproducible per-student in an isolated namespace on the shared cluster. Exact fault mechanism, injection timing, and AI/MaaS backing details are TBD pending the infrastructure phase.
