from agent.scoring import score_job

CRITERIA = {
    "target_titles": {
        "strong_match": ["creative director", "directeur créatif"],
        "weak_match": ["art director", "directeur artistique"],
    },
    "regions": {
        "europe_francophone": {"countries": ["France", "Belgique"]},
    },
    "exclude_keywords": ["junior", "stagiaire"],
}


def test_strong_title_remote_with_salary_scores_high():
    job = {
        "title": "Creative Director",
        "location": "Anywhere",
        "remote": True,
        "description": "Own the creative vision and strategy for the brand.",
        "salary_text": "$100k-$130k",
    }
    score, reasons = score_job(job, CRITERIA)
    assert score >= 90
    assert any("cible" in r for r in reasons)


def test_weak_title_scores_lower_than_strong_title():
    strong_job = {"title": "Creative Director", "location": "France", "remote": False, "description": ""}
    weak_job = {"title": "Art Director", "location": "France", "remote": False, "description": ""}
    strong_score, _ = score_job(strong_job, CRITERIA)
    weak_score, _ = score_job(weak_job, CRITERIA)
    assert strong_score > weak_score


def test_excluded_keyword_penalizes_score():
    job = {"title": "Junior Creative Director", "location": "France", "remote": False, "description": ""}
    score, reasons = score_job(job, CRITERIA)
    assert any("exclu" in r for r in reasons)
    assert score < 40


def test_unknown_location_and_not_remote_gets_no_region_bonus():
    job = {"title": "Creative Director", "location": "Mars", "remote": False, "description": ""}
    score, reasons = score_job(job, CRITERIA)
    assert not any("régions cibles" in r or "compatible" in r for r in reasons)
