"""Source: Remotive public job API (no auth required)."""
import requests

API_URL = "https://remotive.com/api/remote-jobs"


def fetch(query: str = "creative director", limit: int = 50) -> list[dict]:
    try:
        resp = requests.get(API_URL, params={"search": query}, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"[remotive] erreur: {exc}")
        return []

    jobs = resp.json().get("jobs", [])[:limit]
    results = []
    for j in jobs:
        results.append({
            "source": "remotive",
            "title": j.get("title", ""),
            "company": j.get("company_name", ""),
            "location": j.get("candidate_required_location", "Remote"),
            "remote": True,
            "url": j.get("url", ""),
            "description": j.get("description", ""),
            "salary_text": j.get("salary") or None,
            "posted_at": j.get("publication_date", ""),
        })
    return results
