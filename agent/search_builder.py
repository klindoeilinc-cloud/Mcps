"""Génère des liens de recherche prêts à l'emploi pour les plateformes qui
n'ont pas d'API publique (LinkedIn, Welcome to the Jungle, boards africains...).

Ces plateformes interdisent le scraping dans leurs CGU : l'agent ne les
interroge donc jamais automatiquement, il te donne juste le lien à ouvrir.
Les formats d'URL de recherche peuvent évoluer côté plateforme — vérifie
qu'ils retournent bien des résultats.
"""
from urllib.parse import quote_plus


def _q(s: str) -> str:
    return quote_plus(s)


def build_search_plan(profile: dict, criteria: dict) -> list[dict]:
    titles = criteria.get("target_titles", {}).get("strong_match", ["creative director"])
    primary_title_en = next((t for t in titles if "creative director" in t.lower()), titles[0])
    primary_title_fr = next((t for t in titles if "créati" in t.lower()), "directeur créatif")

    plan: list[dict] = []

    plan.append({
        "platform": "LinkedIn Jobs",
        "note": "Recherche remote, tous pays cibles",
        "url": f"https://www.linkedin.com/jobs/search/?keywords={_q(primary_title_en)}&f_WT=2",
    })

    for region in criteria.get("regions", {}).values():
        for country in region.get("countries", [])[:3]:
            if "remote" in country.lower() or "distribué" in country.lower():
                continue
            plan.append({
                "platform": "LinkedIn Jobs",
                "note": f"{primary_title_en} — {country}",
                "url": f"https://www.linkedin.com/jobs/search/?keywords={_q(primary_title_en)}&location={_q(country)}",
            })

    plan.append({
        "platform": "Welcome to the Jungle",
        "note": "Europe francophone, culture d'entreprise détaillée",
        "url": f"https://www.welcometothejungle.com/fr/jobs?query={_q(primary_title_fr)}",
    })
    plan.append({
        "platform": "Indeed France",
        "note": "Marché francophone large",
        "url": f"https://fr.indeed.com/jobs?q={_q(primary_title_fr)}",
    })
    plan.append({
        "platform": "APEC",
        "note": "Cadres, France — filtrer ensuite par rémunération",
        "url": f"https://www.apec.fr/candidat/recherche-emploi.html/emploi?motsCles={_q(primary_title_fr)}",
    })
    plan.append({
        "platform": "We Work Remotely",
        "note": "Remote anglophone, catégorie design/creative",
        "url": "https://weworkremotely.com/categories/remote-design-jobs",
    })
    plan.append({
        "platform": "Wellfound (AngelList)",
        "note": "Startups remote-friendly, anglophone",
        "url": f"https://wellfound.com/jobs?query={_q(primary_title_en)}",
    })
    plan.append({
        "platform": "Emploi.ci",
        "note": "Côte d'Ivoire",
        "url": f"https://www.emploi.ci/recherche-jobs-cote-ivoire?search_keywords={_q(primary_title_fr)}",
    })
    plan.append({
        "platform": "Jobartis",
        "note": "Afrique francophone (Sénégal notamment)",
        "url": f"https://www.jobartis.com/fr/emplois?q={_q(primary_title_fr)}",
    })
    plan.append({
        "platform": "Go Africa Online",
        "note": "Multi-pays Afrique francophone",
        "url": f"https://www.goafricaonline.com/ci/emploi/recherche?q={_q(primary_title_fr)}",
    })
    plan.append({
        "platform": "Google (recherche avancée)",
        "note": "Requête multi-plateformes sur LinkedIn",
        "url": (
            "https://www.google.com/search?q="
            + _q('"directeur créatif" OR "creative director" (remote OR télétravail) site:linkedin.com/jobs')
        ),
    })

    return plan
