# OpenShift 5 workshop — Module 1 and index update

Prepared from `rhpds/openshift-5-container` main commit
`1941145b9ca19fd1afa038ad268e3440eacab359`.

Reference: `rhpds/ocp5-ea-showroom` commit
`c26da5236c4a04526b12e504f779f18672fabe43`, reviewed 20 October 2026.

## Included

- The two updated AsciiDoc pages, at their repository paths.
- `openshift5-module1-index.patch`, containing only those two page changes.
- `preview/index.html`, the Antora-rendered workshop preview. Open this file in a browser after extracting the archive. The preview uses the repository's existing theme; optional web fonts require internet access. The console URL and version are the repository's configured examples, not observed values from a running cluster.

## Apply in Dev Spaces

Extract the ZIP outside your working repository. In the repository terminal, create a working branch, then apply the patch using its extracted path:

```bash
git switch -c docs/module1-hands-on
git apply --check /path/to/extracted/openshift5-module1-index.patch
git apply /path/to/extracted/openshift5-module1-index.patch
git diff --stat
git diff -- content/modules/ROOT/pages/index.adoc content/modules/ROOT/pages/module-01-whats-new-in-ocp5.adoc
```

`/path/to/extracted` is a placeholder for the folder where you extracted the files. If the check fails, compare your current files with the provided versions and reconcile the edits; do not overwrite local work or force the patch. Once reviewed, commit the two files on your branch and use your normal pull-request process.

## Scope and review notes

Module 1 changes from a presentation script to a 20-minute guided exercise. It verifies account access, the reported cluster release, exposed APIs and an AI answer against a small namespace-scoped ConfigMap. Preview feature exploration is optional and depends on the environment.

The index now reflects the actual authoring state: Module 2 is a scaffold, and Modules 3–5 are planned. Their descriptions and durations describe the intended workshop, not completed labs.

The early-access reference uses administrator privileges and a separately provisioned environment. Its administrative mutation exercises have not been carried into the shared-student workflow. No claim of a complete or final OpenShift 5 feature catalogue is made.

GitHub access in this session was read-only. No branch, commit, pull request, or deployment was created remotely.

The Publishing House spec, design, module outline and workflow state were not changed. Some still describe Module 1 as presenter-led. Align them through the normal authoring workflow before formal review. Publishing House service checks were not run because its credentials were not configured here.

## Before delivering the workshop

Use a real participant account to run the module end to end. Confirm the assigned namespace, ConfigMap permissions, console and terminal login, and the cleanup procedure. A working live-inspection exercise additionally needs Lightspeed, a configured LLM and MCP integration with appropriate identity and access controls. A prompt asking for read-only behaviour is not an access-control boundary.

Confirm available observability and preview plugins before selecting an optional tour. Verify the GitOps configuration and namespace layout before writing Module 2. Keep the learner's recorded evidence so later modules can build on what was actually available.

## Validation

- Antora 3.2.1 build passed using the repository's `site.yml` and theme, with errors configured to fail the build.
- All 12 Bash command blocks passed shell syntax validation.
- The page cross-references resolve, and `git diff --check` passed.
- Desktop and mobile previews were rendered and inspected; the content did not overflow the page width.
- The patch passed `git apply --check` against a clean copy of the stated base commit, then applied to produce files byte-for-byte identical to the deliverables.
- Only the requested two pages changed. No OpenShift cluster was available for live execution in this session.
