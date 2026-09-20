"""Scoring heuristique d'une offre par rapport aux critères de config/criteria.yaml.

Le score n'est qu'un tri indicatif : il aide à prioriser, il ne remplace pas
la lecture de l'offre.
"""

STRONG_TITLE_BONUS = 40
WEAK_TITLE_BONUS = 15
EXCLUDE_PENALTY = 50
REGION_BONUS = 25
SENIORITY_BONUS = 15
SALARY_DISCLOSED_BONUS = 20
SALARY_UNKNOWN_BONUS = 10

SENIORITY_KEYWORDS = [
    "strategy", "stratégie", "vision", "leadership",
    "direction créative", "creative vision", "brand strategy",
]


def score_job(job: dict, criteria: dict) -> tuple[int, list[str]]:
    reasons: list[str] = []
    score = 0

    title = (job.get("title") or "").lower()
    desc = (job.get("description") or "").lower()

    target_titles = criteria.get("target_titles", {})
    strong = [t.lower() for t in target_titles.get("strong_match", [])]
    weak = [t.lower() for t in target_titles.get("weak_match", [])]

    if any(t in title for t in strong):
        score += STRONG_TITLE_BONUS
        reasons.append("Titre correspond directement au poste cible (Directeur Créatif+)")
    elif any(t in title for t in weak):
        score += WEAK_TITLE_BONUS
        reasons.append("Titre proche mais potentiellement plus exécutant (à valider)")

    exclude = [x.lower() for x in criteria.get("exclude_keywords", [])]
    if any(x in title for x in exclude):
        score -= EXCLUDE_PENALTY
        reasons.append("Contient un mot-clé exclu (junior/stagiaire/...)")

    location = (job.get("location") or "").lower()
    regions = criteria.get("regions", {})
    all_countries = [c.lower() for r in regions.values() for c in r.get("countries", [])]

    if job.get("remote"):
        score += REGION_BONUS
        reasons.append("Poste remote — compatible avec la cible")
    elif any(c in location for c in all_countries):
        score += REGION_BONUS
        reasons.append(f"Localisation ({job.get('location')}) dans les régions cibles")

    if any(k in desc for k in SENIORITY_KEYWORDS):
        score += SENIORITY_BONUS
        reasons.append("Signaux de séniorité stratégique dans la description")

    salary_text = job.get("salary_text")
    if salary_text:
        score += SALARY_DISCLOSED_BONUS
        reasons.append(f"Salaire indiqué: {salary_text}")
    else:
        score += SALARY_UNKNOWN_BONUS
        reasons.append("Salaire non communiqué — à négocier / clarifier")

    return max(score, 0), reasons
