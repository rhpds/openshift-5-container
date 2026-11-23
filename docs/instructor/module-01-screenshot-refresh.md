# Reviewing the Module 1 screenshots

The [student guide](../../content/modules/ROOT/pages/module-01-whats-new-in-ocp5.adoc) uses captures from the initial deployment and a repeat of the Lightspeed repair in `user-cg6vc-demo`. The [screenshot guide](../../content/modules/ROOT/images/SCREENSHOTS.md) maps each mission to its evidence.

Use these three comparisons to check a refresh.

1. The first ParksMap capture shows a base map before the backend is deployed. The final capture shows clustered markers with the National Parks (PY) layer.
2. The Git build and welcome page establish that HTTP reaches the backend. The data Route separately demonstrates the MongoDB fault and recovery.
3. The Lightspeed action details show the proposed port and the human approval control. The successful write and the subsequent `resources_get` response report the same resource version. A separate Service view establishes the saved port. The terminal capture verifies public API responses. The manual Service repair remains available as a fallback.

The [Mission 5 chat screenshot](../../content/modules/ROOT/images/module01-05-chat-result.jpg) shows Lightspeed confirming the approved Service update. The [instructor preflight](module-01-deployment-preflight.md) explains how to verify the Service if the chat reports an error.
