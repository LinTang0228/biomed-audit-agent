# BioAudit: an agent for auditing biomedical analysis code

**A layered, standards-grounded reviewer for Python and R analysis scripts, focused on statistical validity, study-design soundness, reproducibility, and sound interpretation.**

*Track: Agents for Good.*

---

## Problem and motivation

A substantial share of biomedical findings fail to reproduce, and a recurring cause is not misconduct but ordinary analytical error. A parametric test is applied where its assumptions do not hold; an exposure–outcome association is reported without adjusting for a known confounder; information from the test set leaks into model training and inflates apparent performance; a causal claim is drawn from observational data; a conclusion is stated more strongly than the estimate and its uncertainty support. These errors are common, easy to make, and difficult to catch by reading a results section, because the mistake lives in the analysis code rather than in the prose that describes it.

Two structural facts make the gap persistent. Peer review rarely inspects analysis code, and few research groups have a statistician review every script before submission. The people best placed to catch methodological errors are a scarce resource, and the distance between "the code ran and produced a figure" and "the analysis is valid" is where irreproducible results enter the literature. Data leakage in particular has been documented as a widespread failure mode across hundreds of machine-learning papers spanning many scientific fields (Kapoor and Narayanan, 2023), and much of it is detectable from the code itself.

BioAudit targets this gap. It reviews a single analysis script before its results are trusted or submitted, surfaces the methodological problems it can detect, explains each in plain terms, and proposes a corrected snippet. It is deliberately a static reviewer: it reads code and advises; it does not run the code, and it is designed to assist rather than replace expert statistical review.

## Why an agent

The task is a poor fit for a single prompt and a good fit for a routed set of specialist agents.

- **Intuition.** Reviewing code for statistical validity, study design, leakage, reproducibility, and honest interpretation requires judgement across several distinct concerns, the ability to consult the right domain rules for each, and a way to move from a compact summary into any single issue on demand. A single agent asked to check everything at once must hold all concerns and all rules in view simultaneously, which dilutes attention and raises the chance that a specific issue is missed.
- **Design response.** BioAudit gives each concern its own agent, scoped to one or two areas and supplied only with that area's rules. A study-design-and-statistics agent reasoning over only design and statistics rules is more focused than one prompt juggling six areas.
- **Trade-off.** Multiple agents introduce coordination: their findings must be merged and their severity judgements kept consistent. The design absorbs this with a shared severity scale in the skill and a deterministic merge step. The cost is justified because the alternative — one undifferentiated reviewer — is less reliable on exactly the subtle, area-specific problems that matter most.

## What BioAudit does

The input is one Python or R script (or notebook). The output is organised in two layers.

- **Layer 1, a summary:** one line per finding, grouped by severity (Critical, Important, Minor), compact enough to scan in seconds.
- **Layer 2, a drill-down:** for any finding, the full detail — what the code does that is problematic and why it threatens validity — and a suggested fix shown as a before/after snippet, labelled **mechanical** (a single correct local edit) or **substantive** (a change to the scientific content that the researcher should review).

The deliverable is a single self-contained HTML report: the Layer 1 summary with each finding expandable in place to its Layer 2 detail, using native collapsible elements with no JavaScript and no external assets. A structured JSON report is produced alongside it for programmatic use and for the drill-down and evaluation tools.

The layering addresses the two failure modes of a flat report. A summary keeps every issue visible without producing an unreadable wall of text, and the detail is available for the whole finding set but revealed only where the reader wants depth.

## The audit knowledge base

BioAudit checks six areas: data handling (inspection, missing values, outliers, derived variables, distribution-appropriate summaries); study design (independence of observations, confounding, biased selection); statistics (test choice, assumption checks, multiplicity, effect sizes and confidence intervals); modelling and evaluation (data leakage, metrics, validation, for machine-learning scripts); reproducibility (seeds, file paths, software versions, fragile constructs, hardcoded secrets); and interpretation (conclusions matching the evidence, causal language, selective reporting).

The rules are grounded in established reporting standards rather than ad hoc heuristics: the SAMPL guidelines for statistical reporting, the EQUATOR family of study-type guidelines (CONSORT for trials, STROBE for observational studies, and related), TRIPOD and TRIPOD+AI for prediction models, and the machine-learning-leakage literature. This knowledge is encoded as a portable skill — a control file plus one reference file per area — so that the domain knowledge is separated from the agent code and can be revised without changing the runtime.

## Architecture

A script passes through four stages: routing, parallel checking, deterministic combining, and rendering.

Routing is a deterministic step that detects the language and whether the script performs machine learning. This is the one routing decision that changes which checkers run, and it is reliably detectable from imports and characteristic calls, so it is done in plain code rather than by a model. Three checkers always run — data handling and reproducibility; study design and statistics; interpretation — and a fourth, the data-leakage checker, runs only for machine-learning scripts.

The selected checkers run concurrently as an Agent Development Kit `ParallelAgent`. Each checker is a Gemini agent scoped to one or two areas, given only that area's rules from the skill, constrained to a structured output schema, and instructed to treat the script's contents as data to analyse rather than instructions to follow. Each writes its findings to shared session state.

A deterministic combiner then enforces each checker's scope (dropping any finding outside a checker's areas), removes duplicates, sorts by severity, and assigns identifiers, producing the Layer 1 summary. The Layer 2 renderer and the HTML report build on that structured result.

A single principle runs through the architecture: the parts with one correct answer — routing, scope enforcement, merging, sorting, and rendering — are deterministic code, and the model is reserved for the judgement-heavy work of reading a script against a set of rules.

- **Pros.** This keeps most of the system testable without a model, removes model non-determinism from the merge, and makes the pipeline cheaper and easier to reason about.
- **Cons and applicability.** The router's heuristics can misclassify unusual scripts; coarse routing is reliably pattern-detectable, but fine-grained methodological judgement is not, which is precisely why it is left to the model.

## Design decisions

- **Suggest, do not auto-rewrite.** BioAudit shows a corrected snippet rather than emitting a rewritten file. A corrected file would imply a level of verification the tool cannot provide, since it never runs the code. The tool proposes; the researcher decides and applies. Each fix is labelled mechanical or substantive so the reader knows how much to trust it: mechanical fixes have one correct form, whereas substantive fixes are reasoned proposals about scientific intent and can be wrong.
- **Read, not run.** The tool performs static analysis and does not execute the script. This avoids the safety and reproducibility concerns of running arbitrary user code, but it also sets an honest boundary: with no execution and no access to the data, most checks confirm that a safeguard is present in the code, not that a result is correct.
- **A shared, explicit severity scale.** Critical marks issues likely to make a result wrong as it stands; Important marks issues that could change a result or violate an accepted standard; Minor marks quality gaps unlikely to change conclusions. Holding all checkers to one scale is what makes their merged output coherent.

## Evaluation

Because the review depends on a probabilistic model, its accuracy is measured rather than assumed.

The test set is eleven labelled fixtures. Five are R scripts derived from a real Framingham Heart Study analysis of the association between smoking and systolic blood pressure — an association confounded by age, which the age-adjusted model is intended to expose — with planted issues spanning statistics, study design, coding correctness, reproducibility, and interpretation. Six are Python scripts covering machine learning, differential expression, survival analysis, and classical group comparison. Each fixture carries a documented set of planted issues, and two fixtures are clean controls used to measure the false-positive rate. Comments in the fixtures are deliberately neutral so that the reviewer must detect issues from the code structure rather than from comments that name them.

A machine-readable answer key records the planted issues, and a deterministic scorer matches the system's findings to it at rule-identifier granularity, reporting precision and recall overall and by severity, severity agreement on matched issues, and a separate false-positive count on the control scripts.

The scoring harness and the answer key are verified, and the deterministic components of the system — routing, scope enforcement, merging, rendering, and the skill's coverage of the planted issues — have been executed and checked. The accuracy of the model-dependent checkers is produced by running them over the fixtures and scoring the results: **[pooled precision __, recall __; recall by severity — Critical __, Important __, Minor __; control false positives __; severity agreement __]**. Interpreting these figures, precision on the control scripts is weighted most heavily, because a reviewer that over-flags erodes trust faster than one that misses a minor issue.

## Course concepts demonstrated

Three concepts from the course are demonstrated in the implementation. A **multi-agent system** built with the Agent Development Kit: a parallel set of area-scoped checker agents, with deterministic routing and combining around them. **Agent skills**: the audit knowledge is packaged as a skill — a control file plus per-area reference files — and each checker loads only the rules for its area, an application of progressive disclosure. **Antigravity**: the system is developed and run in the Antigravity IDE, and a single checker can be exercised interactively in the agent development UI.

## Limitations and future work

The limitations are inherent to the approach and are stated plainly.

- The review is static and single-file: no execution, no access to the data, and no cross-file analysis. Consequently, many checks verify that a safeguard is present in the code, not that a result is correct.
- Suggested fixes are reviewed proposals, not verified results; any corrected script must be re-run to confirm it works and that its numbers are sensible.
- The findings come from a non-deterministic model. Critical and Important findings are the stable core; Minor and judgement-based findings vary between runs, and wording varies.
- Deterministic R analysis is narrower than for Python, because R static-analysis tooling is less mature; the judgement-based checks apply equally to both languages.
- Coverage is demonstrated on the fixture set. Real scripts contain issues the fixtures do not represent, and the rule set, while extensible, is not exhaustive.
- BioAudit assists, and does not replace, review by a qualified statistician; it is a rigour aid, not a certification.

Future work follows directly from these limitations: execute code in an ephemeral sandbox to verify proposed fixes and to check results against the data; broaden deterministic R analysis; extend guideline coverage and add reporting-checklist coverage for specific study types; and expand the labelled evaluation set to measure accuracy more precisely.

## Reflection

The project was built in verified stages, each checked before the next. The division between deterministic code and model judgement was not planned at the outset; it emerged as the way to keep most of the system testable and to confine non-determinism to where it is genuinely needed. The least certain part of the system is the checkers' judgement on the subtler design and interpretation rules — for example, recognising immortal-time bias or an uncontrolled confounder from code alone — which is exactly what the evaluation harness exists to measure, and where continued tuning would most improve the tool.

---

*Selected sources: Lang and Altman, SAMPL guidelines for statistical reporting; the EQUATOR Network reporting guidelines (CONSORT, STROBE, and related); Collins and colleagues, TRIPOD+AI; Kapoor and Narayanan, "Leakage and the reproducibility crisis in machine-learning-based science," Patterns, 2023.*
