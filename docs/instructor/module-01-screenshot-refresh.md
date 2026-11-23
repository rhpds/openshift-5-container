# Reviewing the Module 1 screenshots

The [student guide](../../content/modules/ROOT/pages/module-01-whats-new-in-ocp5.adoc) uses captures from the initial deployment and a repeat of the Lightspeed repair in `user-cg6vc-demo`. The [screenshot guide](../../content/modules/ROOT/images/SCREENSHOTS.md) maps each mission to its evidence.

Use these three comparisons to check a refresh.

1. The first ParksMap capture shows a base map before the backend is deployed. The final capture shows clustered markers with the National Parks (PY) layer.
2. The Git build and welcome page establish that HTTP reaches the backend. The data Route separately demonstrates the MongoDB fault and recovery.
3. The Lightspeed action details show the proposed port and the human approval control. The successful write and the subsequent `resources_get` response report the same resource version. A separate Service view establishes the saved port. The terminal capture verifies public API responses. The manual Service repair remains available as a fallback.

The first run returned a chat error after approval even though the Service changed. The student path uses the successful repeat. The [first-run error screenshot](../../content/modules/ROOT/images/module01-05-chat-result.jpg) and [instructor preflight](module-01-deployment-preflight.md) document how to handle that case.
