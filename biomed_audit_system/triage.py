"""
Deterministic triage / routing (no ADK, no model).

The only routing-critical decision is whether the script is a machine-learning /
prediction script, which gates the leakage checker. That is reliably detectable
from imports and characteristic calls, so it is done with heuristics here — which
also makes it unit-testable without a live model. Analysis-type tags are
best-effort and used only for the report header, not for gating.

Limitation: heuristics can misclassify unusual scripts. If robustness matters more
than testability later, this can be replaced or backed by an LLM classifier.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class Triage:
    language: str            # "python" | "r" | "unknown"
    analysis_types: List[str] = field(default_factory=list)
    run_leakage: bool = False


# Strong, specific machine-learning signals. Deliberately excludes bare
# `.fit(` / `.predict(`, which also match statsmodels regression and survival
# fitters and would cause false ML classification.
_ML_MARKERS = [
    r"\bimport\s+sklearn\b", r"\bfrom\s+sklearn\b",
    r"\bimport\s+tensorflow\b", r"\bfrom\s+tensorflow\b",
    r"\bimport\s+torch\b", r"\bfrom\s+torch\b",
    r"\bimport\s+xgboost\b", r"\bfrom\s+xgboost\b",
    r"\bimport\s+lightgbm\b", r"\bfrom\s+lightgbm\b",
    r"\bfrom\s+imblearn\b", r"\bimport\s+keras\b", r"\bfrom\s+keras\b",
    r"\btrain_test_split\b", r"\bcross_val\w*\b",
    r"\b(?:Stratified|Group)?KFold\b", r"\bGridSearchCV\b", r"\bRandomizedSearchCV\b",
    r"\bRandomForest\w*\b", r"\bGradientBoost\w*\b", r"\bLogisticRegression\b",
    r"\bSVC\s*\(", r"\bSMOTE\b", r"\bPipeline\s*\(",
    # R machine-learning
    r"\bcaret\b", r"\btidymodels\b", r"\bglmnet\b", r"\brandomForest\b",
    r"\branger\b", r"\bcreateDataPartition\b", r"\binitial_split\b",
]
_SURVIVAL_MARKERS = [
    r"\blifelines\b", r"\bCoxPHFitter\b", r"\bcoxph\s*\(", r"\bSurv\s*\(",
    r"\bsurvfit\b", r"\bKaplanMeier\b", r"\bWeibullFitter\b",
]
_OMICS_MARKERS = [
    r"\bDESeq\w*\b", r"\bedgeR\b", r"\blimma\b", r"\bvoom\b",
    r"\bscanpy\b", r"\banndata\b",
]
_CLASSICAL_MARKERS = [
    r"\bt\.test\s*\(", r"\bttest_ind\b", r"\baov\s*\(", r"\banova\b",
    r"\blm\s*\(", r"\bglm\s*\(", r"\bols\s*\(", r"\bf_oneway\b",
    r"\bwilcox\w*", r"\bmannwhitney\w*", r"\bchisq\b", r"\bpearsonr\b",
]


def _hit(patterns: List[str], text: str) -> bool:
    return any(re.search(p, text) for p in patterns)


def _guess_language(text: str) -> str:
    if re.search(r"<-", text) or re.search(r"\blibrary\s*\(", text):
        # `<-` and library() are strong R signals; ensure it is not obviously Python
        if not re.search(r"^\s*(import|from)\s+\w", text, re.MULTILINE):
            return "r"
    if re.search(r"^\s*(import|from)\s+\w", text, re.MULTILINE) or re.search(r"\bdef\s+\w+\s*\(", text):
        return "python"
    if re.search(r"<-", text):
        return "r"
    return "unknown"


def classify(script_text: str, filename: str = "") -> Triage:
    ext = Path(filename).suffix.lower() if filename else ""
    if ext == ".r":
        language = "r"
    elif ext in (".py", ".ipynb"):
        language = "python"
    else:
        language = _guess_language(script_text)

    is_survival = _hit(_SURVIVAL_MARKERS, script_text)
    is_ml = _hit(_ML_MARKERS, script_text)
    is_omics = _hit(_OMICS_MARKERS, script_text)
    is_classical = _hit(_CLASSICAL_MARKERS, script_text)

    types: List[str] = []
    if is_ml:
        types.append("machine learning / prediction")
    if is_survival:
        types.append("survival")
    if is_omics:
        types.append("differential expression / omics")
    if is_classical:
        types.append("classical statistics (test / regression)")
    if not types:
        types.append("unclassified")

    # The leakage checker runs only for genuine ML/prediction scripts. `_ML_MARKERS`
    # is specific to ML tooling and excludes bare `.fit(`/`.predict(`, so survival
    # fitting (lifelines/Cox) and statsmodels regression do not trigger it.
    run_leakage = is_ml

    return Triage(language=language, analysis_types=types, run_leakage=run_leakage)
