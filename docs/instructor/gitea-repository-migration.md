# Gitea repository migration for existing workshop students

## Cause

The RHPDS Gitea Operator guards all repository migration with the one-time
Gitea.status.repoMigrationComplete flag. When initial provisioning imports
only openshift-starter-guides, that flag becomes true. Adding
openshift-5-container to automation/gitops/bootstrap-tenant/values.yaml
updates the CR spec but does NOT check/import missing repositories again.

This was reproduced on user-6k7ww-demo. Resetting status alone did not
reconcile. Resetting status and toggling spec.giteaMigrateRepositories
false/true triggered an Ansible playbook run that checked both repos,
imported the missing one and returned HTTP 200; status became true.

## Safe workaround for an existing namespace

Dry run (no writes):

~~~bash
bash automation/scripts/reconcile-gitea-repositories.sh -n user-6k7ww-demo
~~~

Backfill only when the dry run identifies missing repos:

~~~bash
bash automation/scripts/reconcile-gitea-repositories.sh -n user-6k7ww-demo --apply
~~~

Requires oc, jq, curl and an admin/instructor identity with patch permission
for giteas and giteas/status. Only PUBLIC repos with one generated user
are supported. The command reads the Gitea CR but does not print the
admin password or tokens. Do not delete Gitea, PostgreSQL, or PVCs.
Avoid applying this automatically across all student namespaces.

The helper only patches when a repository is missing, triggers the operator,
then checks both live repo availability and the migration completion status.
In a cluster where GitOps self-heals the Gitea CR, check for conflicts
during the brief spec toggle.

## Permanent code fix: RHPDS Gitea Operator

In rhpds/gitea-operator, file roles/gitea-ocp/tasks/main.yml, the last
guard on the Migrate repositories block currently reads:

~~~yaml
- not r_gitea_repos.resources[0].status.repoMigrationComplete | default(false) | bool
~~~

Replace it with a desired-repository-list fingerprint comparison:

~~~yaml
- (_gitea_repositories_list | default([]) | to_json | hash('sha256')) !=
  (r_gitea_repos.resources[0].status.repoMigrationConfigHash | default(''))
~~~

After successfully checking/importing the desired repositories, persist
the fingerprint next to the existing success flag:

~~~yaml
status:
  repoMigrationComplete: true
  repoMigrationConfigHash: "{{ _gitea_repositories_list | default([]) | to_json | hash('sha256') }}"
~~~

Preserve the existing checks for user/admin setup and
migrate_repos.yml's per-repository GET-before-POST logic. With this fix,
changing the repository list triggers a new idempotent migration, while
unchanged configuration remains a no-op. The fingerprint is recorded
only after all checks/imports succeed. Existing CRs without a fingerprint
would recheck their existing repos once after upgrading the operator.

This requires an operator source PR and release through its OLM deployment:
updating the workshop chart alone cannot change operator behavior.
Fingerprint checks do not recover a manually deleted repo when the desired
list is unchanged; continuous drift correction requires periodic comparison
against actual Gitea state.

## Validate

~~~bash
NS=user-6k7ww-demo
GITEA_URL=$(oc get gitea gitea -n "$NS" -o jsonpath='{.status.giteaRoute}')
OWNER=$(oc get gitea gitea -n "$NS" -o jsonpath='{.spec.giteaGenerateUserFormat}')

curl -sS -o /dev/null -w 'HTTP %{http_code}\n' \
  "$GITEA_URL/api/v1/repos/$OWNER/openshift-5-container"
oc get gitea gitea -n "$NS" \
  -o jsonpath='{.status.repoMigrationComplete}{"\n"}'
~~~

Expected: HTTP 200 and true. Then confirm student can edit
content/modules/ROOT/examples/module02-gitops/national-parks-gitops-info.yaml.
