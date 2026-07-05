"""Shared data schema for the biomedical analysis audit system (Stage 3)."""
from __future__ import annotations

from typing import Dict, List, Literal

from pydantic import BaseModel, Field

Area = Literal[
    "data_handling",
    "study_design",
    "statistics",
    "modeling_evaluation",
    "reproducibility",
    "interpretation",
]
Severity = Literal["Critical", "Important", "Minor"]


class Finding(BaseModel):
    id: str = Field(description="Unique tag within a report, e.g. F1.")
    rule_id: str = Field(description="Reference rule id, e.g. STAT-02.")
    area: Area
    severity: Severity
    title: str = Field(description="The problem in <= ~10 words.")
    location: str = Field(description="File and line number(s).")
    what: str
    why: str
    fix_kind: Literal["mechanical", "substantive"]
    suggestion: str
    confidence: Literal["high", "medium"]


class AuditFindings(BaseModel):
    """Output of a single checker."""
    language: Literal["python", "r", "unknown"]
    analysis_type: str
    findings: List[Finding]


class CombinedReport(BaseModel):
    """Output of the combiner: the merged Layer 1 result."""
    language: str
    analysis_types: List[str]
    checkers_run: List[str]
    counts: Dict[str, int]
    findings: List[Finding]
    scope_violations_dropped: int = 0
