# QFPM Multi-Agent

MVP scaffold for a real multi-agent QFPM workflow using the OpenAI Agents SDK.

## Architecture

- **Agent 1 — Data & Performance:** independently researches CR1 Team Performance and CR2 Team Strength.
- **Agent 2 — Market & Valuation:** independently researches CR3 Market Analysis and CR4 Probability & Valuation.
- **Agent 3 — Auditor:** performs a fresh audit, then compares its evidence with the sealed Agent 1 and Agent 2 reports. It owns CR5 and the final verdict.
- **Orchestrator:** starts Agents 1 and 2 concurrently, seals their first reports, manages correction rounds, and enforces the deterministic BET gate.

The first reports are generated in separate `Runner.run()` calls with separate inputs. Neither specialist receives the other specialist's report during round 1. Round 2 is a controlled correction phase; round 3 is the final Agent 3 audit.

## Setup

Python 3.11+ recommended.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
pip install -e ".[dev]"
cp .env.example .env
```

Add your OpenAI API key to `.env`, then run:

```bash
uvicorn qfpm.api:app --reload
```

Open `http://127.0.0.1:8000/docs`.

## Run an analysis

POST `/analyze`:

```json
{
  "competition": "English Championship",
  "kickoff_date": "2026-11-03",
  "timezone": "Asia/Bangkok",
  "matches": [
    {
      "home": "Preston North End",
      "away": "Sheffield United",
      "asian_handicap": "Sheffield United -0.5",
      "odds": 2.06,
      "odds_source": "user-supplied",
      "odds_timestamp": "2026-11-03T17:20:00+07:00"
    }
  ]
}
```

The odds fields are optional, but no BET can be approved without verified AH line and odds, a full probability distribution, AH settlement probabilities, fair odds, and positive EV. A model's narrative confidence is not a substitute for any of these.

## Important configuration notes

- `QFPM_MODEL` defaults to `gpt-4.1`; change it to a model enabled for your OpenAI API project if needed.
- This scaffold uses the SDK's hosted `WebSearchTool` for independent web research. Add licensed football data feeds (fixtures, xG, lineups, injuries, odds history) before production use.
- Search results are evidence leads, not automatically verified facts. Agent 3 must cite URLs and timestamps and flag conflicts.
- Do not place API keys in source code or commit `.env`.
- This is research software, not an automated betting execution system. No bookmaker account integration or bet placement is included.

## QFPM rules encoded

Exactly five Core Rules:
1. CR1 Team Performance
2. CR2 Team Strength
3. CR3 Market Analysis
4. CR4 Probability & Valuation
5. CR5 Final Validation

Standard qualification: at least 3/5 Core Rules pass. PARTIAL and NOT_VERIFIED do not count as PASS.

CR1 priority: Agent 3 may permit an analysis to be displayed when CR1 evidence is credible, even if the total score is below 3/5. This does not qualify the match and never overrides the BET gate.

The BET gate is enforced in Python, not entrusted to the final LLM wording.
