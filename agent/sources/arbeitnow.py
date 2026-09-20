"""Source: Arbeitnow public job board API (no auth required)."""
import requests

API_URL = "https://www.arbeitnow.com/api/job-board-api"


def fetch(query: str = "creative director", limit: int = 50) -> list[dict]:
    try:
        resp = requests.get(API_URL, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"[arbeitnow] erreur: {exc}")
        return []

    data = resp.json().get("data", [])
    q = query.lower()
    filtered = [j for j in data if q in j.get("title", "").lower()]

    results = []
    for j in filtered[:limit]:
        results.append({
            "source": "arbeitnow",
            "title": j.get("title", ""),
            "company": j.get("company_name", ""),
            "location": j.get("location", ""),
            "remote": bool(j.get("remote", False)),
            "url": j.get("url", ""),
            "description": j.get("description", ""),
            "salary_text": None,
            "posted_at": j.get("created_at", ""),
        })
    return results
