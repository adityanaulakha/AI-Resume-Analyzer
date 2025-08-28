import json
from app import parse_response

def test_parse_valid_json():
    sample = json.dumps({
        "matched_skills": [{"skill": "React", "note": "Core UI framework used"}],
        "missing_skills": [{"skill": "TypeScript", "note": "Not mentioned"}],
        "match_percentage": 55,
        "justification": "Some frontend plus gaps",
        "summary": "Solid base with gaps."
    })
    data = parse_response(sample)
    assert data["match_percentage"] == 55
    assert data["matched_skills"][0]["skill"].lower() == "react"

def test_parse_fallback_sections():
    # Simulate a non-JSON model output
    raw = """Matched Skills:\n- React: Used in recent project\n- Git: Version control\n\nMissing Skills:\n- TypeScript: Not listed\n\nMatch Percentage: 60% (Missing TS)\n\nSummary:\nGood start, needs TS."""
    data = parse_response(raw)
    assert data["match_percentage"] == 60
    assert any(s["skill"].lower() == "react" for s in data["matched_skills"])
    assert any(s["skill"].lower() == "typescript" for s in data["missing_skills"])
