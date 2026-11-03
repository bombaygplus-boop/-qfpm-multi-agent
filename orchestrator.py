import asyncio, hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path
from agents import Runner, trace
from .agents import agent_1, agent_2, agent_3
from .schemas import SlateInput, SpecialistReport, AuditorReport
from .gates import enforce_bet_gate

MAX_ROUNDS = min(int(os.getenv("QFPM_MAX_ROUNDS", "3")), 3)
RUNS_DIR = Path("runs")
RUNS_DIR.mkdir(exist_ok=True)

def _dump(model):
    return model.model_dump(mode="json")

def _seal(payload: dict, path: Path) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()
    digest = hashlib.sha256(raw).hexdigest()
    path.write_text(json.dumps({"sha256": digest, "payload": payload}, ensure_ascii=False, indent=2))
    return digest

async def _run_specialist(agent, prompt: str) -> SpecialistReport:
    result = await Runner.run(agent, prompt)
    return result.final_output

async def _run_auditor(prompt: str) -> AuditorReport:
    result = await Runner.run(agent_3, prompt)
    return result.final_output

async def analyze_slate(slate: SlateInput) -> dict:
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    base_prompt = (
        "Analyze this QFPM slate independently. Round 1. Do not assume missing data.\n"
        + slate.model_dump_json(indent=2)
    )
    with trace("QFPM Multi-Agent Workflow", metadata={"run_id": run_id}):
        # TRUE BLIND FIRST PASS: separate agents, separate calls, concurrent execution.
        report_1, report_2 = await asyncio.gather(
            _run_specialist(agent_1, base_prompt),
            _run_specialist(agent_2, base_prompt),
        )

        sealed_1 = _seal(_dump(report_1), RUNS_DIR / f"{run_id}_agent1_round1.json")
        sealed_2 = _seal(_dump(report_2), RUNS_DIR / f"{run_id}_agent2_round1.json")

        audit_prompt = f'''
Perform Round 1 independent audit. Start with your own fresh research.
Only after your independent findings, compare these sealed specialist reports.
Original slate:
{slate.model_dump_json(indent=2)}
Agent 1 sealed report SHA256: {sealed_1}
Agent 1 report:
{report_1.model_dump_json(indent=2)}
Agent 2 sealed report SHA256: {sealed_2}
Agent 2 report:
{report_2.model_dump_json(indent=2)}
'''
        audit_1 = await _run_auditor(audit_prompt)
        _seal(_dump(audit_1), RUNS_DIR / f"{run_id}_agent3_round1.json")

        # Round 2: only targeted correction requests; original round-1 reports remain immutable.
        if MAX_ROUNDS >= 2 and (audit_1.corrections_for_agent_1 or audit_1.corrections_for_agent_2):
            correction_1 = "Round 2 targeted corrections only. Preserve original findings unless new evidence changes them.\n" + "\n".join(audit_1.corrections_for_agent_1) + "\nSlate:\n" + slate.model_dump_json()
            correction_2 = "Round 2 targeted corrections only. Preserve original findings unless new evidence changes them.\n" + "\n".join(audit_1.corrections_for_agent_2) + "\nSlate:\n" + slate.model_dump_json()
            report_1_r2, report_2_r2 = await asyncio.gather(
                _run_specialist(agent_1, correction_1),
                _run_specialist(agent_2, correction_2),
            )
            _seal(_dump(report_1_r2), RUNS_DIR / f"{run_id}_agent1_round2.json")
            _seal(_dump(report_2_r2), RUNS_DIR / f"{run_id}_agent2_round2.json")
        else:
            report_1_r2, report_2_r2 = report_1, report_2

        # Round 3: final auditor rechecks; no further correction cycle.
        final_prompt = f'''
Round 3 FINAL AUDIT. Independently recheck critical evidence and issue final verdict.
Do not assume prior reports are correct. No further routine research loops.
Original slate:
{slate.model_dump_json(indent=2)}
Agent 1 original sealed report:
{report_1.model_dump_json(indent=2)}
Agent 2 original sealed report:
{report_2.model_dump_json(indent=2)}
Agent 1 Round 2:
{report_1_r2.model_dump_json(indent=2)}
Agent 2 Round 2:
{report_2_r2.model_dump_json(indent=2)}
Agent 3 Round 1:
{audit_1.model_dump_json(indent=2)}
'''
        final_audit = await _run_auditor(final_prompt)
        final_audit.match_verdicts = [enforce_bet_gate(v) for v in final_audit.match_verdicts]
        final_hash = _seal(_dump(final_audit), RUNS_DIR / f"{run_id}_agent3_final.json")

    return {
        "run_id": run_id,
        "architecture": "parallel_blind_specialists_then_independent_audit",
        "rounds_max": MAX_ROUNDS,
        "sealed_report_hashes": {
            "agent_1_round_1": sealed_1,
            "agent_2_round_1": sealed_2,
            "agent_3_final": final_hash,
        },
        "agent_1": _dump(report_1),
        "agent_2": _dump(report_2),
        "agent_1_round_2": _dump(report_1_r2),
        "agent_2_round_2": _dump(report_2_r2),
        "agent_3_round_1": _dump(audit_1),
        "final_audit": _dump(final_audit),
    }
