# Stage 2 — Statistics & study-design checker

One checker, end to end: an ADK `LlmAgent` that reads a Python or R analysis
script and reports **Area 2 (study design)** and **Area 3 (statistics)** issues
from the Stage 1 skill, as structured findings. Other areas are out of scope by
design and handled by their own checkers in later stages.

## Files
- `stats_design_checker/agent.py` — schema (`Finding`, `AuditFindings`), skill-rule
  loading, and the agent (`root_agent`).
- `stats_design_checker/__init__.py` — exposes `root_agent`.
- `run_checker.py` — feeds one script to the agent and prints the Layer 1 summary
  and the raw JSON.
- `requirements.txt` — dependencies.

## Setup
1. Place the Stage 1 skill folder (`biomed_audit_skill/`) somewhere accessible.
2. Install dependencies (in Antigravity via the Agents CLI, or directly):
   `pip install -r requirements.txt`.
3. Set environment variables:
   - `GOOGLE_API_KEY` — your AI Studio key.
   - `BIOAUDIT_MODEL` — a Gemini model your key supports (default `gemini-2.5-flash`;
     adjust to what is available to you).
   - `BIOAUDIT_SKILL_DIR` — path to `biomed_audit_skill/` (otherwise the agent
     searches upward from its own location).

## Running it
**Primary (measurement) — the runner**, which numbers the script's lines so the
model can cite them:
```
python run_checker.py ../fhs_fixtures/fhs_02_stat_assumptions.R
```
It prints the Layer 1 summary followed by the full findings JSON.

**Interactive — the ADK dev UI** (robust across ADK versions):
```
adk web
```
Open the local URL it prints, select `stats_design_checker`, and paste a script
(ideally with `N| ` line prefixes) into the chat.

## Expected outputs (targets to check against)
These are what a **correct** run should produce, derived from the fixtures'
ground truth and the Stage 1 rules. They are the scoring targets — not an
observed run (this checker was not executed here; see the verification note).
Critical/Important in-scope items are the stable targets; Minor and
judgement-based items may vary between runs.

**`fhs_02_stat_assumptions.R`** — expect **2 findings (+1 optional Minor)**:
- `STAT-02` Important (line 15): pooled t-test (`var.equal = TRUE`) with the
  equal-variance assumption unchecked; variances actually differ.
- `STAT-04` Important (lines 16–18): only a p-value reported — no effect size, CI,
  statistic, or df.
- `STAT-01` Minor (line 15), *optional*: parametric test with no distribution
  check / large-n justification unstated.
- **Must NOT appear** (out of scope): the SEM-as-spread issue (that is `DATA-05`,
  a data-handling matter for another checker). If it appears, the scope
  instruction needs tightening.

**`fhs_03_confounding.R`** — expect **1 finding**:
- `DESIGN-01` Important–Critical (line 6): `lm(SBP ~ smoke)` omits age, though
  confounding by age is the explicit subject and age is available.
- **Must NOT appear** (out of scope): the causal-language claim (that is
  `INTERP-01`, for the interpretation checker).

**`test_04_survival.py`** — expect **3 findings**:
- `DESIGN-04` Critical (line 12): `treated` defined from `drug_start_day` (a
  post-baseline event) → immortal-time bias. *This is the judgement-heaviest
  detection and the one most likely to be missed.*
- `STAT-02` Important (lines 14–15): proportional-hazards assumption never tested.
- `STAT-04` Minor–Important (lines 17–18): hazard ratio reported without a CI.
- **Must NOT appear** (out of scope): the hardcoded absolute path (`REPRO-02`).

**`test_02_omics_diffexp.py`** — expect **4 findings**: `DESIGN-03` (batch
confounded with condition), `DESIGN-02` (pseudoreplication via repeated
`sample_id`), `STAT-03` (2000 tests, no correction), `STAT-01` (t-test on raw
counts).

**`fhs_01_clean.R`** (control) — expect **0 findings** from this checker (its only
borderline issue, `DATA-05`, is out of scope here).

## Scoring
For each script, compare the run to the target by `rule_id` and approximate
location:
- **TP** — a target rule reported.
- **FP** — an extra finding, especially an out-of-scope one or any finding on the
  control. Out-of-scope FPs are scope failures and matter as much as accuracy.
- **FN** — a target rule missed (watch `DESIGN-04`).

Precision = TP / (TP + FP); Recall = TP / (TP + FN). If either is low, tune the
instruction (Stage 2 iteration) before Stage 3. Two dials usually suffice:
tightening the scope paragraph (fewer out-of-scope FPs) and strengthening the
judgement rules' phrasing (fewer FNs on `DESIGN-*`).

## Honest caveats
- **Not executed here.** This sandbox has no ADK, no API key, and restricted
  network, so the agent has not been run against a live model. Syntax, rule
  loading, the schema, the scope design, and the output formatter were verified
  (see `STAGE2_VERIFICATION.md`); live behaviour is what you measure.
- **Model non-determinism.** Wording, Minor findings, and borderline judgements
  will vary run to run; the Critical/Important in-scope items are the stable core.
- **ADK version drift.** `Runner`/session call signatures change across releases.
  If `run_checker.py` errors on a signature, use `adk web`, or adjust to your
  installed API (the ADK docs MCP server in Antigravity can confirm current
  usage).
- **`output_schema` constraint.** Setting a structured `output_schema` disables
  tool use / agent transfer for this agent in current ADK. That is fine here (the
  rules are embedded in the instruction, no tools needed), but keep it in mind for
  later stages.
