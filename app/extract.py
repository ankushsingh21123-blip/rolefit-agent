"""Rule-based preference extraction.

Used by the stub LLM (demo mode / tests) and as the fallback when the
real LLM's structured output cannot be parsed. It is deliberately
boring: keyword and regex matching against a fixed vocabulary, so its
behaviour is deterministic and unit-testable. The Gemini path uses the
LLM for the same job; both produce a ``ProfilePatch``.
"""

import re

from .models import ProfilePatch

_SKILL_ALIASES: dict[str, str] = {
    "python": "Python",
    "fastapi": "FastAPI",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "docker": "Docker",
    "react": "React",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "css": "CSS",
    "sql": "SQL",
    "excel": "Excel",
    "data analytics": "Data Analytics",
    "analytics": "Data Analytics",
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "figma": "Figma",
    "ui/ux": "UI/UX",
    "ui ux": "UI/UX",
    "ux": "UI/UX",
    "prototyping": "Prototyping",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "node": "Node.js",
    "rest apis": "REST APIs",
    "rest api": "REST APIs",
    "content writing": "Content Writing",
    "seo": "SEO",
    "english": "English",
    "social media": "Social Media",
    "google ads": "Google Ads",
    "communication": "Communication",
    "crm": "CRM",
    "sales": "Sales",
    "negotiation": "Negotiation",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "aws": "AWS",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "testing": "Testing",
    "selenium": "Selenium",
    "statistics": "Statistics",
    "business analysis": "Business Analysis",
    "recruitment": "Recruitment",
    "hr": "HR",
    "operations": "Operations",
    "logistics": "Logistics",
    "c++": "C++",
    "game development": "Game Development",
    "react native": "React Native",
    "technical writing": "Technical Writing",
    "documentation": "Documentation",
    "etl": "ETL",
    "photoshop": "Photoshop",
    "illustration": "Illustration",
    "product management": "Product Management",
    "troubleshooting": "Troubleshooting",
    "llms": "LLMs",
    "llm": "LLMs",
    "rag": "RAG",
}

_LOCATION_ALIASES: dict[str, str] = {
    "bengaluru": "Bengaluru",
    "bangalore": "Bengaluru",
    "hyderabad": "Hyderabad",
    "mumbai": "Mumbai",
    "bombay": "Mumbai",
    "delhi": "Delhi NCR",
    "pune": "Pune",
    "chennai": "Chennai",
    "gurugram": "Gurugram",
    "gurgaon": "Gurugram",
    "remote": "Remote",
}

_ROLE_PHRASES: list[str] = [
    "data analyst",
    "data scientist",
    "data engineer",
    "backend",
    "frontend",
    "front end",
    "full stack",
    "machine learning",
    "devops",
    "product designer",
    "ui/ux",
    "content writer",
    "technical writer",
    "business analyst",
    "operations",
    "customer support",
    "sales",
    "graphic designer",
    "product manager",
    "software engineer",
    "python developer",
    "react developer",
    "support engineer",
    "marketing",
    "designer",
    "developer",
    "engineer",
    "analyst",
    "writer",
]

_STOPWORDS = {
    "a", "an", "the", "any", "work", "job", "jobs", "role", "roles",
    "or", "and", "with", "for", "of", "in", "on", "to", "do", "doing",
}


def _find_all(text: str, phrases: dict[str, str]) -> list[str]:
    found: list[str] = []
    for phrase, canonical in phrases.items():
        pattern = r"(?<![a-z0-9])" + re.escape(phrase) + r"(?![a-z0-9])"
        if re.search(pattern, text):
            found.append(canonical)
    return found


def _find_salary(text: str) -> int | None:
    # "₹40,000", "at least 30k", "₹60,000 or more", "minimum 25k"
    candidates: list[int] = []
    for match in re.finditer(r"₹\s*([\d,]+)", text):
        try:
            value = int(match.group(1).replace(",", ""))
        except ValueError:
            continue
        if 1_000 <= value <= 500_000:
            candidates.append(value)
    for match in re.finditer(
        r"(?:at least|minimum|above|over|more than|or more)\D{0,12}?(\d+)\s*k\b",
        text,
    ):
        value = int(match.group(1)) * 1000
        if 1_000 <= value <= 500_000:
            candidates.append(value)
    for match in re.finditer(r"(\d+)\s*k\s*(?:per month|/month|a month|monthly)", text):
        value = int(match.group(1)) * 1000
        if 1_000 <= value <= 500_000:
            candidates.append(value)
    return candidates[0] if candidates else None


_CANONICAL_NEVER: list[tuple[str, list[str]]] = [
    ("night shift", ["night shift", "night shifts", "night-shift", "night work", "overnight"]),
    ("weekends", ["weekend", "weekends"]),
    ("sales", ["sales"]),
    ("support", ["support", "customer support"]),
    ("calls", ["call", "calls", "calling", "phone"]),
    ("field work", ["field", "field work", "field sales"]),
    ("targets", ["target", "targets", "incentive"]),
]


def _find_never(text: str) -> list[str]:
    never: list[str] = []
    # Look only inside refusal tails ("never X", "no X", "don't want X",
    # "do not want X", "avoid X", "not X"), so a skill mentioned as a
    # want is never mistaken for a refusal.
    for match in re.finditer(
        r"(?:never|no|don't want|do not want|avoid|not)\s+([^.,;!?\n]+)", text
    ):
        tail = match.group(1).strip()
        for canonical, variants in _CANONICAL_NEVER:
            if any(variant in tail for variant in variants):
                never.append(canonical)
        for piece in re.split(r"\s+or\s+|\s+and\s+|,", tail):
            token = piece.strip().lower()
            token = re.sub(r"^(a|an|the|any)\s+", "", token)
            if len(token) >= 3 and token not in _STOPWORDS:
                never.append(token)
    # dedupe, keep order
    seen: set[str] = set()
    result: list[str] = []
    for token in never:
        if token not in seen:
            seen.add(token)
            result.append(token)
    return result


def extract_profile_rules(message: str) -> ProfilePatch:
    """Deterministic extraction from one user message."""
    text = message.lower()
    skills = _find_all(text, _SKILL_ALIASES)
    locations = _find_all(text, _LOCATION_ALIASES)

    employment_types: list[str] = []
    if "part-time" in text or "part time" in text:
        employment_types.append("Part-time")
    if "full-time" in text or "full time" in text:
        employment_types.append("Full-time")
    if "internship" in text or "intern" in text:
        employment_types.append("Internship")

    work_modes: list[str] = []
    if "remote" in text:
        work_modes.append("Remote")
    if "hybrid" in text:
        work_modes.append("Hybrid")
    if (
        "on-site" in text
        or "onsite" in text
        or "in-office" in text
        or "in office" in text
    ):
        work_modes.append("On-site")

    roles = _find_all(text, {phrase: phrase for phrase in _ROLE_PHRASES})
    roles = ["frontend" if r == "front end" else r for r in roles]

    return ProfilePatch(
        wants_text=message.strip()[:200],
        role_keywords=roles,
        skills=skills,
        locations=locations,
        min_salary_monthly=_find_salary(text),
        employment_types=employment_types,
        work_modes=work_modes,
        never=_find_never(text),
        notes=[],
    )
