from qfpm.schemas import FinalMatchVerdict, GateCheck
from qfpm.gates import enforce_bet_gate

def test_bet_denied_if_any_critical_gate_missing():
    v = FinalMatchVerdict(
        match="A vs B",
        core_rules={f"CR{i}": "PASS" for i in range(1, 6)},
        core_rules_passed=5,
        qualifies=True,
        critical_gate=GateCheck(
            verified_ah_line_and_odds=True,
            probability_distribution_poisson=True,
            ah_settlement_probabilities=True,
            fair_odds=True,
            ev_calculated_and_positive=False,
        ),
        bet_approved=True,
        verdict="BET",
        rationale=[],
    )
    out = enforce_bet_gate(v)
    assert out.bet_approved is False
    assert out.verdict == "NO BET"

def test_bet_requires_three_core_rules():
    v = FinalMatchVerdict(
        match="A vs B",
        core_rules={f"CR{i}": "PASS" for i in range(1, 6)},
        core_rules_passed=2,
        qualifies=False,
        critical_gate=GateCheck(
            verified_ah_line_and_odds=True,
            probability_distribution_poisson=True,
            ah_settlement_probabilities=True,
            fair_odds=True,
            ev_calculated_and_positive=True,
        ),
        bet_approved=True,
        verdict="BET",
        rationale=[],
    )
    out = enforce_bet_gate(v)
    assert out.bet_approved is False
    assert out.verdict == "NO BET"
