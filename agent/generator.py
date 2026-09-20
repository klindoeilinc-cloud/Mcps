"""Génération de CV et lettres de motivation adaptés, via l'API Claude.

Règle de sécurité éditoriale : on demande explicitement au modèle de ne
jamais inventer d'expérience, de chiffre ou de nom d'entreprise absent du
profil fourni. Toute information manquante doit apparaître comme
[PLACEHOLDER À COMPLÉTER] plutôt que d'être fabriquée.
"""
import os

import yaml
from anthropic import Anthropic

DEFAULT_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5")

NO_FABRICATION_RULE = (
    "N'invente jamais une expérience, un chiffre, un nom d'entreprise ou une "
    "compétence absente du PROFIL DU CANDIDAT fourni ci-dessous. Si une "
    "information utile manque, insère un placeholder explicite entre crochets, "
    "par exemple [CHIFFRE D'IMPACT À AJOUTER], plutôt que de la fabriquer."
)


def _client() -> Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY manquant. Copie .env.example vers .env et "
            "renseigne ta clé API Anthropic."
        )
    return Anthropic(api_key=api_key)


def _profile_to_yaml(profile: dict) -> str:
    return yaml.dump(profile, allow_unicode=True, sort_keys=False)


def draft_cv(profile: dict, job: dict, region_norms: str, mcps_methodology: str, lang: str = "fr") -> str:
    client = _client()
    lang_label = "français" if lang == "fr" else "anglais"

    prompt = f"""Tu es un expert en recrutement créatif et en storytelling de carrière.

{NO_FABRICATION_RULE}

PROFIL DU CANDIDAT :
{_profile_to_yaml(profile)}

MÉTHODOLOGIE PROPRIÉTAIRE DU CANDIDAT (fil rouge stratégique, à utiliser sans la sur-expliquer) :
{mcps_methodology}

OFFRE D'EMPLOI CIBLE :
Titre : {job.get('title')}
Entreprise : {job.get('company')}
Lieu : {job.get('location')}
Description :
{(job.get('description') or '')[:4000]}

RÈGLES D'ADAPTATION RÉGIONALE :
{region_norms}

CONSIGNE :
Rédige un CV en {lang_label}, au format Markdown, qui positionne le candidat comme un
Directeur Créatif stratège — pas un exécutant créatif — en t'appuyant strictement sur
les faits du profil. Adapte la longueur, le ton et la structure aux normes régionales
pertinentes pour cette offre.
"""
    resp = client.messages.create(
        model=DEFAULT_MODEL,
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text


def draft_cover_letter(profile: dict, job: dict, region_norms: str, mcps_methodology: str, lang: str = "fr") -> str:
    client = _client()
    lang_label = "français" if lang == "fr" else "anglais"

    prompt = f"""Tu es un expert en recrutement créatif et en storytelling de carrière.

{NO_FABRICATION_RULE}

PROFIL DU CANDIDAT :
{_profile_to_yaml(profile)}

MÉTHODOLOGIE PROPRIÉTAIRE DU CANDIDAT (fil rouge stratégique, à utiliser sans la sur-expliquer) :
{mcps_methodology}

OFFRE D'EMPLOI CIBLE :
Titre : {job.get('title')}
Entreprise : {job.get('company')}
Lieu : {job.get('location')}
Description :
{(job.get('description') or '')[:4000]}

RÈGLES D'ADAPTATION RÉGIONALE :
{region_norms}

CONSIGNE :
Rédige une lettre de motivation en {lang_label}, au format Markdown, structurée en
3 à 4 paragraphes courts (pourquoi cette entreprise / pourquoi ce candidat / valeur
apportée / prochaine étape). Le ton et le niveau de formalité doivent suivre les
normes régionales pertinentes pour cette offre. Ne jamais paraphraser l'offre :
montrer une compréhension de son enjeu business et créatif réel.
"""
    resp = client.messages.create(
        model=DEFAULT_MODEL,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text
