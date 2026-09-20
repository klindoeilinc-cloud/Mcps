"""Suivi du pipeline de candidatures dans un CSV local (data/pipeline.csv)."""
import csv
from datetime import date
from pathlib import Path

FIELDS = [
    "date_added", "company", "title", "region", "source",
    "url", "score", "status", "next_action", "notes",
]
DEFAULT_PATH = Path("data/pipeline.csv")


def _ensure_file(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with path.open("w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=FIELDS).writeheader()


def add_entry(entry: dict, path: Path = DEFAULT_PATH) -> None:
    _ensure_file(path)
    row = {k: entry.get(k, "") for k in FIELDS}
    if not row.get("date_added"):
        row["date_added"] = date.today().isoformat()
    with path.open("a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=FIELDS).writerow(row)


def load(path: Path = DEFAULT_PATH) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def update_status(company: str, title: str, status: str, next_action: str = "", path: Path = DEFAULT_PATH) -> None:
    rows = load(path)
    updated = False
    for r in rows:
        if r["company"].strip().lower() == company.strip().lower() and r["title"].strip().lower() == title.strip().lower():
            r["status"] = status
            if next_action:
                r["next_action"] = next_action
            updated = True
    if not updated:
        raise ValueError(f"Aucune candidature trouvée pour {company} / {title}")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def report(path: Path = DEFAULT_PATH) -> str:
    rows = load(path)
    if not rows:
        return "Aucune candidature suivie pour le moment. Utilise `track add` pour commencer."

    counts: dict[str, int] = {}
    for r in rows:
        status = r.get("status") or "(sans statut)"
        counts[status] = counts.get(status, 0) + 1

    lines = [f"Total candidatures suivies : {len(rows)}", ""]
    for status, n in sorted(counts.items(), key=lambda x: -x[1]):
        lines.append(f"- {status}: {n}")
    return "\n".join(lines)
