# Stage 6 verification - integration and evaluation

Stage 6 delivers the end-to-end wiring, the evaluation harness, and the top-level
README. The scoring logic and the answer key are deterministic and were executed
and verified here; producing actual precision/recall requires the live run.

## A. Verified here (executed)
1. **Syntax** - `eval/evaluate.py`, `eval/run_all.py`, and the rewritten
   `run_audit.py` compile.
2. **Answer key** - `answer_key.json` loads; 11 fixtures, 37 planted rule-entries
   at rule-id granularity (multi-instance rules such as `MODEL-01`, which fires on
   scaling/feature-selection/SMOTE, count once - a deliberate granularity choice
   stated in the file).
3. **Scorer logic** - `score_fixture` was checked on constructed reports:
   - a perfect run scores TP = expected, FP = FN = 0, full severity agreement;
   - a run with one missing rule and one spurious rule scores FN = 1, FP = 1 with
     the correct rule ids;
   - a severity disagreement is counted in the agreement metric but not as a
     miss;
   - a control with a spurious Critical scores a false positive; a control with
     only a Minor is tolerated (no false positive).
4. **Scorecard end-to-end** - `evaluate()` over a mock reports directory prints the
   per-fixture table, the control section, pooled precision/recall, recall by
   severity, severity agreement, and a list of missing reports.
5. **End-to-end wiring** - `run_audit --json --html` compiles and chains
   audit -> saved JSON -> HTML (the audit step needs a live model; the JSON and
   HTML writing reuse the verified Stage 5 renderer).

## B. What remains (requires a live model)
The one outstanding measurement: run the checkers against a live Gemini model over
the fixtures and score the results. This yields the actual precision/recall - the
numbers this environment could not produce.

## C. Procedure to produce the numbers
```
export GOOGLE_API_KEY=...  BIOAUDIT_MODEL=...  BIOAUDIT_SKILL_DIR=/path/to/biomed_audit_skill
python -m biomed_audit_system.eval.run_all fhs_fixtures test_fixtures   # saves eval/reports/*.json
python -m biomed_audit_system.eval.evaluate                            # prints the scorecard
```
Then read off pooled precision/recall, recall by severity, control false
positives, and severity agreement. If precision is low, tighten the checker scope
paragraphs; if recall is low on judgement rules (e.g. `DESIGN-04`), strengthen
their phrasing; re-run.

## Conclusion
The evaluation harness is complete and its scoring is verified against the answer
key; the end-to-end wiring is in place. The only step left is the live run that
turns the verified harness into measured precision/recall - which is also the
measurement that closes out the remaining risk in Stages 2-3.
