from .schemas import FinalMatchVerdict, GateCheck

def enforce_bet_gate(verdict: FinalMatchVerdict) -> FinalMatchVerdict:
    gate = verdict.critical_gate
    gate_pass = all([
        gate.verified_ah_line_and_odds,
        gate.probability_distribution_poisson,
        gate.ah_settlement_probabilities,
        gate.fair_odds,
        gate.ev_calculated_and_positive,
    ])
    verdict.bet_approved = bool(verdict.bet_approved and gate_pass and verdict.qualifies)
    if not verdict.bet_approved and verdict.verdict == "BET":
        verdict.verdict = "NO BET"
        verdict.rationale.append(
            "Python safety gate overrode BET: qualification and all Critical Rule Gate checks are mandatory."
        )
    return verdict
