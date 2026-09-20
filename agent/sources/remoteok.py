"""Source: RemoteOK public job API (no auth required)."""
import requests

API_URL = "https://remoteok.com/api"


def fetch(query: str = "creative director", limit: int = 50) -> list[dict]:
    headers = {"User-Agent": "mcps-job-agent/1.0"}
    try:
        resp = requests.get(API_URL, headers=headers, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"[remoteok] erreur: {exc}")
        return []

    data = resp.json()
    jobs = [d for d in data if isinstance(d, dict) and "position" in d]

    q = query.lower()
    filtered = [
        j for j in jobs
        if q in (j.get("position", "") + " " + " ".join(j.get("tags", []))).lower()
    ]

    results = []
    for j in filtered[:limit]:
        raw_url = j.get("url", "")
        results.append({
            "source": "remoteok",
            "title": j.get("position", ""),
            "company": j.get("company", ""),
            "location": j.get("location", "Remote"),
            "remote": True,
            "url": raw_url if raw_url.startswith("http") else f"https://remoteok.com{raw_url}",
            "description": j.get("description", ""),
            "salary_text": j.get("salary") or None,
            "posted_at": j.get("date", ""),
        })
    return results
