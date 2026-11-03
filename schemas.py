from typing import Literal
from pydantic import BaseModel, Field

RuleStatus = Literal["PASS", "PARTIAL", "FAIL", "NOT_VERIFIED"]

class MatchInput(BaseModel):
    home: str
    away: str
    asian_handicap: str | None = None
    odds: float | None = Field(default=None, gt=1.0)
    odds_source: str | None = None
    odds_timestamp: str | None = None

class SlateInput(BaseModel):
    competition: str
    kickoff_date: str
    timezone: str = "Asia/Bangkok"
    matches: list[MatchInput]

class EvidenceItem(BaseModel):
    claim: str
    source_name: str | None = None
    url: str | None = None
    published_at: str | None = None
    checked_at: str | None = None
    confidence: Literal["HIGH", "MEDIUM", "LOW"] = "LOW"
    notes: str | None = None

class ChecklistResult(BaseModel):
    item: str
    status: RuleStatus
    finding: str
    evidence_ids: list[int] = []

class MatchAssessment(BaseModel):
    match: str
    proposed_market: str | None = None
    core_rules: dict[str, RuleStatus]
    checklist: list[ChecklistResult]
    evidence: list[EvidenceItem]
    data_confidence: int = Field(ge=0, le=100)
    handicap_confidence: int = Field(ge=0, le=100)
    betting_value_assessment: str
    risks: list[str] = []
    missing_data: list[str] = []
    requested_corrections: list[str] = []

class SpecialistReport(BaseModel):
    agent_name: str
    role: str
    round_number: int
    assessments: list[MatchAssessment]
    overall_notes: list[str] = []

class GateCheck(BaseModel):
    verified_ah_line_and_odds: bool = False
    probability_distribution_poisson: bool = False
    ah_settlement_probabilities: bool = False
    fair_odds: bool = False
    ev_calculated_and_positive: bool = False

class FinalMatchVerdict(BaseModel):
    match: str
    core_rules: dict[str, RuleStatus]
    core_rules_passed: int = Field(ge=0, le=5)
    qualifies: bool
    cr1_data_credible_for_display: bool = False
    analysis_display_allowed: bool = False
    critical_gate: GateCheck
    bet_approved: bool = False
    verdict: Literal["BET", "NO BET", "INSUFFICIENT DATA"]
    rationale: list[str]
    unresolved_conflicts: list[str] = []
    missing_data: list[str] = []

class AuditorReport(BaseModel):
    agent_name: str = "Agent 3"
    round_number: int
    independent_findings: list[EvidenceItem]
    match_verdicts: list[FinalMatchVerdict]
    corrections_for_agent_1: list[str] = []
    corrections_for_agent_2: list[str] = []
    final_notes: list[str] = []
