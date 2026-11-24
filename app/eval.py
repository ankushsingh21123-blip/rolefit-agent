"""LLM eval harness: a golden set of person-want -> expected-match cases.

Run it with ``python -m app.eval`` (from the repo root) or through
``POST /evaluate``. It drives the agent exactly as a user would — one
or two chat turns per case — and scores the top 3:

- hit@3: at least one expected job in the top 3
- MRR@5: mean reciprocal rank of the first expected job in the top 5
- violations: forbidden (deal-breaker) jobs appearing in the top 3

With the demo providers (stub LLM + hash embeddings) the run is fully
deterministic and needs no API key. With Gemini configured it measures
the real pipeline instead.
"""

import json
import sys

from .agent import Agent
from .eval_cases import EVAL_CASES
from .models import EvalCaseResult, EvalReport


def run_eval(agent: Agent) -> EvalReport:
    agent.ensure_seeded()
    results: list[EvalCaseResult] = []
    for case in EVAL_CASES:
        session_id = f"eval-{case['id']}"
        response = None
        for message in case["messages"]:
            response = agent.chat(session_id, message, top_k=5)
        top_ids = [item.job.id for item in (response.jobs if response else [])]
        expected = case["expected"]
        forbidden = case["forbidden"]
        hit = any(job_id in top_ids[:3] for job_id in expected)
        rank = 0
        for index, job_id in enumerate(top_ids):
            if job_id in expected:
                rank = index + 1
                break
        reciprocal = 1.0 / rank if rank else 0.0
        violations = sorted(set(top_ids[:3]) & set(forbidden))
        results.append(
            EvalCaseResult(
                case_id=case["id"],
                hit_at_3=hit,
                reciprocal_rank=reciprocal,
                violations=violations,
                top_job_ids=top_ids,
            )
        )
    n = len(results)
    return EvalReport(
        cases=results,
        hit_at_3=sum(1 for r in results if r.hit_at_3) / n if n else 0.0,
        mrr_at_5=sum(r.reciprocal_rank for r in results) / n if n else 0.0,
        violation_count=sum(len(r.violations) for r in results),
        llm_provider=agent.llm.name,
        embedding_provider=agent.embedder.name,
    )


def main() -> int:
    from .agent import build_agent
    from .config import get_settings

    report = run_eval(build_agent(get_settings()))
    print(
        f"hit@3: {report.hit_at_3:.2f}  "
        f"MRR@5: {report.mrr_at_5:.2f}  "
        f"violations: {report.violation_count}  "
        f"({report.llm_provider} + {report.embedding_provider})"
    )
    for case in report.cases:
        mark = "PASS" if case.hit_at_3 and not case.violations else "FAIL"
        print(
            f"  [{mark}] {case.case_id}: top3={case.top_job_ids[:3]} "
            f"violations={case.violations}"
        )
    print(json.dumps(report.model_dump(), indent=1))
    failed = [c for c in report.cases if not c.hit_at_3 or c.violations]
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
