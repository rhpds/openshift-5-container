# Module 2: GitOps — Deploy and Auto-Sync the National Parks Full Stack

## Overview

This is the **main required Module 2 student experience**, not an optional extension.
Students use Gitea, the **GA OpenShift GitOps 1.22 console plug-in** and
Lightspeed 2.0 to deploy an independent ParksMap frontend, Python API and
MongoDB 8 database into their GitOps namespace, then commit a Git change
and see Argo CD reconcile it **automatically**.

The Module 1 National Parks app stays untouched in
`user-<guid>-demo`. The new stack deploys to
`user-<guid>-gitops`, which is created **before class by the privileged
tenant-bootstrap GitOps** — not by a student's Argo CD controller.

## Audience and duration

- **Personas:** Kubernetes/OpenShift beginners to intermediate platform engineers
  and SREs; comfortable with basic Git, deployments, services and namespaces
- **Prerequisites:** Completed Module 1, working student Gitea account,
  separate GitOps namespace, GitOps console plug-in, PVC StorageClass,
  Python Docker BuildConfig and accessible images
- **Duration:** 45 minutes for students after instructor preflight

## Learning objectives

1. Identify the difference between Argo CD control-plane namespace and
   Application destination namespace.
2. Read a Kustomize tree that describes a **complete three-tier application**:
   three Deployments, Services, two Routes, BuildConfig/ImageStream,
   PVC, bootstrap Jobs and scoped RBAC.
3. Create or update an Argo CD Application **using the OpenShift GitOps console**,
   with automated sync/self-heal enabled and automatic prune disabled.
4. Observe OpenShift build the Python image, create MongoDB credentials in
   the destination namespace, deploy the workloads and populate park data.
5. Commit a safe ConfigMap change to Gitea and verify it automatically
   reconciles to Kubernetes **without manual synchronization**.
6. Verify source and live data, the two independent app stacks and student RBAC
   boundaries using Lightspeed read-only MCP evidence and the OpenShift CLI.

## Student missions

| Mission | Activity | Time |
|---|---|---:|
| 1 | Verify student identity, two projects, Lightspeed resources | 5 min |
| 2 | Explore root Kustomization and complete fullstack/ source in Gitea | 7 min |
| 3 | Create Auto-Sync Application from OpenShift GitOps console | 10 min |
| 4 | Watch Python build, PVC, database, Routes and dataset initialization | 15 min |
| 5 | Commit Gitea ConfigMap change, observe Auto-Sync and check isolation | 8 min |

## Source and Application

**Main source path:**
`content/modules/ROOT/examples/module02-gitops`

The root kustomization.yaml must contain `resources: - fullstack`.
The complete stack remains in
`content/modules/ROOT/examples/module02-gitops/fullstack/`.
The old single-ConfigMap file in the root directory is not part of the
active Kustomization.

**Argo CD Application:** national-parks-settings

- Application CR namespace: `user-<guid>-demo`
- Destination namespace: `user-<guid>-gitops`
- Source repo: student's **editable Gitea clone**, tracking main
- Auto-Sync: enabled; Self-Heal: enabled; automatic pruning: disabled
- RespectIgnoreDifferences: enabled for the backend image field changed
  by the OpenShift ImageStream trigger

## Security and infrastructure boundaries

- The privileged tenant GitOps bootstrap owns namespace creation and
  management label; no student cluster-scoped Namespace creation.
- No NetworkPolicy is created in this module. RBAC and optional cluster
  network-isolation mechanisms must not be conflated.
- MongoDB Secret is generated locally by a dedicated namespaced Job with
  restrictive ServiceAccount/Role/RoleBinding, not stored in Git.
- MongoDB 8 uses the correct Service port 27017 and a disposable 1Gi PVC.
- ParksMap discovery uses read-only Service/Route permissions.
- PostSync dataset loading only calls the destructive load endpoint if the
  collection is empty. Never use the load endpoint as a health check.
- The student's Gitea main must contain the updated root and fullstack/
  files before creating the Application. Existing Gitea repos are not mirrors.
- No expectation that students manually Sync or patch Deployments. The
  application is reconciled automatically; Lightspeed uses read tools.

## Instructor release gates

Before delivery, validate with two real student identities, confirm a working
default StorageClass and image build/pull, and synchronize **all** student
Gitea copies. A bulk sync attempt reported AUTH_FAILED on all ten pushes on
13 November 2026; updating upstream GitHub alone will not fix stale copies.
Capture genuine OpenShift 5 console screenshots for S01–S12 and validate
that park markers appear in the GitOps namespace.

Modules 3 and 5 need to account for the complete workload being GitOps-owned,
because direct edits to these Deployments can be reverted by Self-Heal.
