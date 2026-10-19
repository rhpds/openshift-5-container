# Editorial Review — Module 1: What's New in OCP 5

## module-reviewer Results

| ID | Severity | Finding |
|----|----------|---------|
| E.5 | ~~High~~ FIXED | `ocp_version: '5.0.0-rc.1'` added to `content/antora.yml`. |
| C.6 / D.8 | Medium | Em dashes (—) at lines 6, 24, 47, 109. Replace with parentheses or commas per Red Hat style. Example: line 6 "presenter-led module — approximately 20 minutes" → "presenter-led module (approximately 20 minutes)". |
| D.6 | Medium | Numbers 0–9 written as words: "two hours" (line 25), "three nodes" (line 41), "one management cluster" (line 46), "one parent namespace" (line 116). Replace with numerals. |
| C.9 | Warning | 17 headings use title case instead of sentence case. Capitalise only the first word and proper nouns. Examples: "Learning Objectives" → "Learning objectives"; "Hosted Control Planes" → "Hosted control planes"; "Key Takeaways" → "Key takeaways". Product names stay capitalised. |
| D.2 | Warning | "OCP" first appears at line 1 (the title) without expansion. First use in body text should read "OpenShift Container Platform (OCP)". |
| B.9 | Warning | 0 hands-on exercises; minimum is 2 for a workshop module. Module is deliberately presenter-led — document this intentional absence if acceptable, or add a short participant activity (credential check, structured discussion). |

### Passed

- B.8 — 3 learning objectives present
- B.11 — learning objectives use bullet list format
- B.13 — no `== References` in non-conclusion module
- C.1/C.2 — no `image::` macros
- C.3 — no bare external links
- C.4 — xref at line 184 correctly omits `^`
- C.5 — code block uses `[source,yaml]`
- C.7 — all lists separated by blank lines
- C.8 — document title uses single `=`
- C.10 — no `include::` macros
- D.1 — "the Red Hat OpenShift Platform" not found
- D.3/D.4 — no vague or superlative terms
- D.5 — no non-inclusive terms
- D.7 — Oxford comma used correctly
- D.9 — no gendered pronouns
- D.10 — all version references use `{ocp_version}`, not hardcoded strings
- E.1 — no `oc` commands
- E.2 — YAML block uses consistent 2-space indentation
- E.3/E.3a/E.3b — YAML block exempt from `role="execute"` requirement
- E.4 — no hardcoded cluster URLs, usernames, or passwords
- E.7 — heading levels progress correctly (no skips)
- E.9 — YAML example is syntactically valid

---

## Spec Alignment

| Check | Status | Notes |
|-------|--------|-------|
| SA-1: Outline Coverage | PASS | All 6 outline sections present and in order. No scope creep detected. |
| SA-2: Learning Objectives | PASS | All 3 module-level objectives have corresponding content. |
| SA-3: Duration Alignment | PASS | 185 lines of presenter narrative is appropriate for 20 minutes of delivery. |
| SA-4: Cross-Module Consistency | SKIP | Only one module reviewed. |

## Red Hat Style

| Check | Status | Notes |
|-------|--------|-------|
| RS-1: Product Names | PASS | "OpenShift Lightspeed", "Red Hat OpenShift GitOps", "Operator Lifecycle Manager v1" all used correctly. OCP abbreviation flagged under D.2 above. |
| RS-2: Version Consistency | PASS | All version references use `{ocp_version}` attribute consistently (D.10 passed). |

---

## Summary

- High: 1
- Medium: 2 (em dashes, word-form numbers)
- Warning: 3 (heading case, OCP abbreviation, no exercises)

## Recommended Actions

1. **Fix (antora.yml):** Add `ocp_version: '5.0'` under `asciidoc.attributes` — this is the only High issue and will cause visible rendering failures without it.
2. **Fix (module):** Replace em dashes at lines 6, 24, 47, 109 with parentheses or commas.
3. **Fix (module):** Replace word-form numbers with numerals at lines 25, 41, 46, 116.
4. **Fix (module):** Convert 17 headings from title case to sentence case.
5. **Consider (module):** Expand "OCP" on first body-text use to "OpenShift Container Platform (OCP)".
6. **Consider (module):** Either add a short participant activity or explicitly accept the zero-exercise warning for this presenter-led module.
