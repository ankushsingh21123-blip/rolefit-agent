"""Rule-based extraction: deterministic, no LLM needed."""

from app.extract import extract_profile_rules


def test_extracts_skills_locations_salary():
    patch = extract_profile_rules(
        "I want a remote Python backend job, at least ₹40,000 a month."
    )
    assert "Python" in patch.skills
    assert "Remote" in patch.locations
    assert patch.min_salary_monthly == 40000
    assert "Remote" in patch.work_modes


def test_extracts_k_salary():
    patch = extract_profile_rules("Frontend React role, minimum 30k a month.")
    assert patch.min_salary_monthly == 30000
    assert "React" in patch.skills


def test_extracts_never_tokens():
    patch = extract_profile_rules(
        "I never want sales or customer support calls."
    )
    assert "sales" in patch.never
    assert "support" in patch.never
    assert "calls" in patch.never


def test_extracts_night_shift_and_weekends():
    patch = extract_profile_rules(
        "No night shifts, no weekends, please."
    )
    assert "night shift" in patch.never
    assert "weekends" in patch.never


def test_extracts_employment_and_roles():
    patch = extract_profile_rules(
        "I'm looking for a part-time data analyst internship."
    )
    assert "Part-time" in patch.employment_types
    assert "Internship" in patch.employment_types
    assert "data analyst" in patch.role_keywords


def test_want_is_not_mistaken_for_never():
    patch = extract_profile_rules("I want a customer support role in Hyderabad.")
    assert patch.never == []
    assert "Hyderabad" in patch.locations
