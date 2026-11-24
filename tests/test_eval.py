"""Eval harness: the golden set must pass end to end."""

from app.eval import run_eval


def test_eval_golden_set_passes(agent):
    report = run_eval(agent)
    assert report.hit_at_3 == 1.0, [
        (c.case_id, c.top_job_ids[:3]) for c in report.cases if not c.hit_at_3
    ]
    assert report.violation_count == 0, [
        (c.case_id, c.violations) for c in report.cases if c.violations
    ]
    assert report.mrr_at_5 > 0.5
