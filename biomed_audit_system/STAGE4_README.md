# Stage 4 - The fix step (Layer 2 drill-down)

The drill-down layer: given the Layer 1 report from Stage 3, expand a selected
finding (or set) into full detail with a suggested fix. Deterministic; no model.

## What it does
Each checker (Stages 2-3) already emits `what`, `why`, `fix_kind`, and a
before/after `suggestion` for its findings. Stage 4 presents that on demand and
adds:
- the **trust framing** - `MECHANICAL` (single correct local edit; safe after a
  quick check) vs `SUBSTANTIVE` (changes the scientific content; review before
  accepting);
- the standard **read-not-run caveat** on every fix;
- a **validation flag** when a suggestion looks malformed (empty, or no clear
  before/after).

Layer 1 stays one line per finding; Layer 2 expands only what you select.

## Design decision (and its trade-off)
Fixes are produced once, by the checkers, and Stage 4 surfaces them on demand.
This keeps Stages 2-3 unchanged and makes Stage 4 fully deterministic and testable
without a model. The alternative - generating each fix on demand in a dedicated
fix agent - would defer token cost to only the findings you open and could tailor
the snippet more tightly to the code, at the cost of another model call and more
behaviour that cannot be verified without a model. Given the correctness-first
priority and the "suggest-only, shown in place" decision, Stage 4 is deterministic;
the on-demand variant remains an option.

## Files
- `layer2.py` - rendering, selection, trust framing, caveat, suggestion validation.
- `drilldown.py` - CLI that renders Layer 2 from a saved report JSON (no model).

## Usage
1. Produce a report with the full system and save its JSON block:
   ```
   python -m biomed_audit_system.run_audit ../fhs_fixtures/fhs_04_coding_bugs.R
   # copy the printed JSON into report.json
   ```
2. Drill down (no model needed):
   ```
   python -m biomed_audit_system.drilldown report.json F3
   python -m biomed_audit_system.drilldown report.json --severity Critical
   python -m biomed_audit_system.drilldown report.json --all
   ```

## Output shape (per finding)
```
--------------------------------------------------------------------
[Critical] Reversed smoking-status coding    (id F1, DATA-07, high)
Area: data_handling
Location: fhs_04_coding_bugs.R:7

What: ...
Why:  ...

Suggested fix - MECHANICAL - a single correct local edit; safe to apply after a quick check.
    - fhs$smoke <- ifelse(fhs$CIG > 0, 0, 1)
    + fhs$smoke <- ifelse(fhs$CIG > 0, 1, 0)
    Rationale: matches the 1=smoker definition.

Note: this tool read the code but did not run it. Treat the fix as a reviewed
proposal, not a verified result - re-run the corrected script to confirm.
```

## The boundary this stage cannot cross (important)
Stage 4 validates the **format** of a suggestion (present, has a before/after) and
frames how much to trust it. It cannot verify the suggestion is **correct** - the
fix text is produced by the checkers (Stages 2-3) with a live model, and the tool
never runs the code. So a suggested fix is a reviewed proposal, not a guarantee.
This is the same read-not-run limitation, made explicit at the fix layer, and is
why substantive fixes are labelled for review and every fix carries the caveat.
