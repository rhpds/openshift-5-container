# Operating Applications on OpenShift 5: Platform Engineering, AI & GitOps

<!-- This file is the design document for your lab or demo. -->
<!-- Fill in each section below, or run /rhdp-publishing-house to have the intake skill help. -->
<!-- Sections marked with [brackets] are placeholders — replace with real content. -->
<!-- The validation gate checks for all required sections before submission. -->

## Overview

This hands-on lab puts attendees in the role of a platform team responsible for onboarding and operating applications on a shared OpenShift 5 environment. It exists to show how GitOps, multitenancy controls, and AI-assisted observability come together to run a production platform day-to-day, including the OpenShift 4 → 5 improvements to platform management, observability, multitenancy, and workload lifecycle. Participants will onboard an application via GitOps, apply namespace-level access/network/resource controls, manage workloads competing for shared platform resources, investigate an injected production issue using metrics/logs/events/traces and OpenShift Lightspeed, validate the AI's recommendations against real cluster data, and push the final fix back through GitOps.

## Target Audience

- **Role:** Platform engineers / SREs responsible for onboarding and operating applications on a shared OpenShift platform
- **Experience level:** Intermediate
- **What they already know:** Core OpenShift/Kubernetes concepts (pods, deployments, namespaces, basic RBAC), basic Git usage, general troubleshooting instincts
- **What they don't know:** GitOps-driven onboarding and multitenancy enforcement, managing resource contention with quotas/limit ranges/priority classes, using OpenShift Lightspeed alongside metrics/logs/traces to investigate incidents, and pushing validated fixes back through a GitOps workflow

## Prerequisites

- Familiarity with core OpenShift/Kubernetes concepts (pods, deployments, namespaces, RBAC) and basic Git usage
- Can the lab validate these automatically? No — trust-based; no automated prerequisite check is planned

## Learning Objectives

1. Configure application onboarding through GitOps (ArgoCD), including namespace, RBAC, and NetworkPolicy creation
2. Verify tenant isolation holds between student namespaces after onboarding
3. Manage resource contention across shared workloads using ResourceQuotas, LimitRanges, and PriorityClasses
4. Analyze workload resource usage on a shared cluster and right-size deployments accordingly
5. Troubleshoot an injected production incident using OpenShift Lightspeed together with metrics, logs, and traces
6. Verify OpenShift Lightspeed's recommendations against real cluster data before acting on them
7. Implement a validated fix declaratively through GitOps and confirm recovery
8. Monitor rollout health and ArgoCD sync status while performing a rolling update

<!-- Scale to duration: up to 3 objectives per 45 min of content. Start with action verbs: Configure, Deploy, Create, Implement, Troubleshoot, Monitor, Scale. Each should be testable. NOT: Understand, Learn, Know. -->

## Content Type

Lab (hands-on)

## Products & Technologies

- Red Hat OpenShift Container Platform (version 5.x)
- Red Hat OpenShift GitOps (ArgoCD)
- OpenShift Lightspeed (AI-assisted troubleshooting assistant) — not yet in the product catalog; flagged for content/infra review confirmation

<!-- Use official names: "Red Hat OpenShift", not "OpenShift". List upstream projects separately. -->

## Module Map

| Module | Title | Duration |
|--------|-------|----------|
| 1 | What's New in OCP 5 (orientation, no hands-on) | 20 min |
| 2 | GitOps Onboarding & Multitenancy | 20 min |
| 3 | Workload Management & Resource Controls | 20 min |
| 4 | AI-Assisted Incident Investigation | 40 min |
| 5 | GitOps Remediation & App Lifecycle | 20 min |
| — | **Total hands-on** | **~100 min** |
| — | Intro / presentation (Module 1) | ~20 min |
| — | **Total lab** | **~2 hours** |

<!-- Each module 10-30 min. Total: lab 1-4 hours, demo 15-45 min. Modules should build on each other. -->

## Difficulty Level

Intermediate

## Environment

**Learner view:** Each student is assigned an isolated namespace on a shared, multi-user OpenShift 5 cluster (30 concurrent students on one cluster). Authentication, OpenShift GitOps (ArgoCD), and OpenShift Lightspeed are pre-deployed before the lab starts; the sample application is not yet present — students onboard it themselves via GitOps in Module 2.

**Automation needed:** Yes

- Per-user namespace, RBAC, and quota scaffolding for up to 30 concurrent students
- ArgoCD bootstrap for GitOps onboarding/remediation flows
- OpenShift Lightspeed deployment
- A pre-built sample application workload with an injectable fault for the Module 4 incident scenario

## Infrastructure Requirements

- **Cloud provider:** TBD — confirmed in infrastructure phase
- **Cluster type:** TBD — confirmed in infrastructure phase
- **OCP version:** TBD — confirmed in infrastructure phase
- **Topology:** TBD — confirmed in infrastructure phase
- **Sizing:** TBD — confirmed in infrastructure phase
- **Automation approach:** TBD — confirmed in infrastructure phase
- **AI/MaaS:** TBD — confirmed in infrastructure phase
- **External services:** TBD — confirmed in infrastructure phase
- **AAP version:** TBD — confirmed in infrastructure phase
- **Non-GA products:** TBD — confirmed in infrastructure phase

<!-- Not all fields must be known at intake. "TBD, estimating ~X" is fine. -->

## Assessment Strategy (Optional)

<!-- Optional — skip this section for demos or classic labs without verification. -->
<!-- Relevant for Zero-Touch labs with solve/validate buttons or labs with automated checks. -->

Trust-based. This is a classic (non-Zero-Touch) lab with no solve/validate automation planned — students confirm success visually via the OpenShift console (tenant isolation, resource dashboards, ArgoCD sync status, application recovery) rather than through scripted checks.
