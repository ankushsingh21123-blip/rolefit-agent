"""Deterministic retrieval + reranking.

The vector search returns candidates; this module decides what the
person actually sees. Deal-breakers are hard filters (a job that
violates one never appears), everything else is a weighted score with
a plain-words reason attached to each match, so the ranking can be
explained and tested without an LLM in the loop.

score = 0.40 * vector similarity
      + 0.35 * skill overlap with the stated skills
      + 0.25 * preference fit (location, employment type, work mode,
        salary floor)
"""

from .models import Job, PreferenceProfile, RankedJob
from .store import RetrievedJob


def _norm(text: str) -> str:
    return text.lower().replace("-", " ").replace("_", " ")


def _job_text(job: Job) -> str:
    return _norm(
        f"{job.title} {job.company} {job.description} {' '.join(job.skills)}"
    )


def _token_matches(token: str, text: str) -> bool:
    token = _norm(token).strip()
    if not token:
        return False
    if token in text:
        return True
    # tolerate singular/plural differences ("weekend" vs "weekends")
    if token.endswith("s") and token[:-1] in text:
        return True
    if (token + "s") in text:
        return True
    return False


def violates_deal_breaker(profile: PreferenceProfile, job: Job) -> str | None:
    """Return the violated rule as a short string, or None if the job
    passes every hard filter."""
    text = _job_text(job)
    for token in profile.never:
        if _token_matches(token, text):
            return f"deal-breaker: {token}"
    if (
        profile.min_salary_monthly is not None
        and job.salary_max < profile.min_salary_monthly
    ):
        return f"salary below ₹{profile.min_salary_monthly:,}/month minimum"
    if profile.employment_types and job.employment_type not in profile.employment_types:
        return "employment type"
    # Work mode is a soft preference, not a deal-breaker: a hybrid role in
    # the person's city is still worth showing when they asked for remote,
    # and vice versa. It is scored in score_job instead.
    if profile.locations:
        if job.location in profile.locations:
            pass
        elif job.work_mode == "Remote":
            # A remote job can be done from any of the person's places.
            pass
        else:
            return "location"
    return None


def score_job(
    profile: PreferenceProfile, job: Job, vector_score: float
) -> tuple[float, list[str]]:
    """Weighted score in [0, 1] plus plain-words reasons."""
    reasons: list[str] = []
    score = 0.0

    vector = max(0.0, min(1.0, vector_score))
    score += 0.40 * vector
    if vector >= 0.5:
        reasons.append("Strong semantic match for what you described")

    profile_skills = {s.lower() for s in profile.skills}
    if profile_skills:
        matched = [s for s in job.skills if s.lower() in profile_skills]
        frac = len(matched) / max(len(profile_skills), 1)
        score += 0.35 * frac
        if matched:
            noun = "skill" if len(matched) == 1 else "skills"
            reasons.append(f"Matches your {', '.join(matched)} {noun}")
    else:
        score += 0.35 * 0.5

    pref = 0.0
    if profile.locations:
        if job.location in profile.locations:
            pref += 0.10
            reasons.append(f"In {job.location}")
        elif job.work_mode == "Remote":
            pref += 0.10
            if "Remote" in profile.locations:
                reasons.append("Remote, as you asked")
            else:
                reasons.append("Remote — works from anywhere")
    else:
        pref += 0.05
    if profile.employment_types:
        if job.employment_type in profile.employment_types:
            pref += 0.05
            reasons.append(f"{job.employment_type}, as you asked")
    else:
        pref += 0.025
    if profile.work_modes:
        if job.work_mode in profile.work_modes:
            pref += 0.05
            reasons.append(f"{job.work_mode}, as you asked")
    else:
        pref += 0.025
    if profile.min_salary_monthly is not None:
        if job.salary_min >= profile.min_salary_monthly:
            pref += 0.05
            reasons.append(
                f"Pays ₹{job.salary_min:,}–₹{job.salary_max:,} a month, "
                f"above your ₹{profile.min_salary_monthly:,} minimum"
            )
        elif job.salary_max >= profile.min_salary_monthly:
            pref += 0.025
            reasons.append(
                f"Pays up to ₹{job.salary_max:,} a month, around your minimum"
            )
    else:
        pref += 0.025
    score += min(pref, 0.25)

    return round(min(max(score, 0.0), 1.0), 4), reasons


def rerank(
    profile: PreferenceProfile,
    candidates: list[RetrievedJob],
    top_k: int = 5,
) -> list[RankedJob]:
    """Hard-filter deal-breakers, score the rest, return the top-k."""
    ranked: list[RankedJob] = []
    for candidate in candidates:
        if violates_deal_breaker(profile, candidate.job) is not None:
            continue
        score, reasons = score_job(profile, candidate.job, candidate.score)
        ranked.append(RankedJob(job=candidate.job, score=score, reasons=reasons))
    ranked.sort(key=lambda r: (-r.score, r.job.id))
    return ranked[:top_k]
