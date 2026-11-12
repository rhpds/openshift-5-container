# Module 1 final screenshot refresh

This is a **draft image-only follow-up** to
[`docs/module01-mission3-screenshots`](https://github.com/waynedovey/openshift-5-container/tree/docs/module01-mission3-screenshots).

## Three actual student screenshots

Copy the three prepared images into `content/modules/ROOT/images/`:

| Screenshot | Destination | Placement |
|---|---|---|
| Student terminal login, password removed | `module01-student-login-success.png` | Mission 0, immediately after `oc login` |
| National Parks map with populated markers | `module01-s01-map.png` | Mission 6, successful map |
| OpenShift topology of all three workloads | `module01-s02-topology.png` | Mission 6, three healthy workloads |

The originals were captured from a disposable student project. **Never commit
the original terminal screenshot:** it exposes a workshop password. Use only
the sanitized PNG supplied in the screenshot bundle.

## Upload

Download `module01-screenshots-pr-assets.zip` from the ChatGPT conversation.
It has exactly the repository paths needed. On the screenshot branch, run:

```bash
unzip -o module01-screenshots-pr-assets.zip
git add content/modules/ROOT/images/module01-student-login-success.png \
        content/modules/ROOT/images/module01-s01-map.png \
        content/modules/ROOT/images/module01-s02-topology.png
git commit -m "Add final student login, working map and topology screenshots"
git push
```

Do not mark the PR ready until the three PNG blobs are visible in GitHub and
the rendered Showroom page displays them. Do not confuse unchanged legacy
placeholder images with the new uploads.

## Quick review

1. The login screenshot shows `Login successful` with the password redacted.
2. S01 shows the National Parks (PY) map layer and park markers.
3. S02 shows the frontend, Python backend and MongoDB together in Topology.
4. The screenshot paths match the student guide's `image::` references.
