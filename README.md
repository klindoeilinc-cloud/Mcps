# MCPS Job Agent

Agent de recherche d'emploi pour piloter ta transition de Directeur Artistique exécutant vers **Directeur Créatif stratège**, en Afrique francophone, Europe francophone et Europe anglophone (remote ou présentiel).

L'agent ne remplace pas ta réflexion : il **diagnostique le marché, transforme tes candidatures, pilote ton pipeline et mesure tes résultats** — exactement la logique de ta méthodologie MCPS, appliquée à ta propre recherche de poste.

## Ce que fait l'agent

1. **`discover`** — interroge des APIs publiques d'offres d'emploi (Remotive, RemoteOK, Arbeitnow), les score selon tes critères (titre, région, séniorité, salaire), et génère une liste de liens de recherche prêts à l'emploi pour les plateformes sans API publique (LinkedIn, Welcome to the Jungle, APEC, boards africains, etc.).
2. **`draft`** — à partir du texte d'une offre, génère un CV et une lettre de motivation adaptés (langue, format, ton) à la région ciblée, en s'appuyant sur ton profil réel et sur ta méthodologie MCPS comme narrative de positionnement.
3. **`track`** — journalise et pilote ton pipeline de candidatures (CSV), avec un rapport de synthèse.

### Ce que l'agent ne fait pas

- Il ne scrape pas LinkedIn ou les autres plateformes qui l'interdisent dans leurs CGU : il génère des **liens de recherche directs** que tu ouvres toi-même (`discover` les affiche à chaque exécution).
- Il n'invente **aucun fait biographique** : `generator.py` instruit explicitement Claude de ne jamais inventer une expérience, un chiffre ou une entreprise absente de `config/profile.yaml`, et d'insérer un `[PLACEHOLDER]` explicite si une information manque.

## Installation

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# renseigne ANTHROPIC_API_KEY dans .env
```

## Étape 0 — indispensable avant tout : complète ta configuration

- `config/profile.yaml` : ton vrai parcours, réalisations chiffrées, portfolio, langues, prétentions salariales.
- `config/criteria.yaml` : régions ciblées, titres de poste, mots-clés à exclure, benchmarks de salaire indicatifs.
- `config/mcps_methodology.md` : le détail réel de ta méthodologie (le fichier fourni est un squelette basé sur "Diagnostiquer / Transformer / Piloter / Mesurer" — enrichis-le avec tes outils et cas concrets).

Sans ça, l'agent tourne mais produit des candidatures génériques ou trouées de placeholders.

## Utilisation

```bash
# 1. Découvrir des offres + obtenir les liens de recherche manuelle
python -m agent.cli discover --query "creative director" --min-score 40 --save

# 2. Générer CV + lettre pour une offre précise (copie le texte de l'annonce dans un fichier)
python -m agent.cli draft --job-file offres/acme.txt --company "Acme" --title "Creative Director" \
  --location "Abidjan / Remote" --lang fr --out-dir candidatures/acme

# 3. Suivre le pipeline
python -m agent.cli track add --company "Acme" --title "Creative Director" --region afrique_francophone --status "à postuler"
python -m agent.cli track update --company "Acme" --title "Creative Director" --status "entretien 1"
python -m agent.cli track report
```

## Feuille de route avant décembre 2026

- **Semaine 1** : compléter `profile.yaml` et `criteria.yaml` avec tes données réelles ; enrichir `mcps_methodology.md`.
- **Chaque semaine** : `discover` → sélectionner les meilleures offres → `draft` → postuler → `track add`.
- **Toutes les 2 semaines** : `track report`, ajuster `criteria.yaml` (régions, salaire minimum, mots-clés) selon les retours du marché.
- **Fin novembre** : revue complète du pipeline, itération sur le CV/lettre type si le taux de réponse est faible.

## Pistes d'évolution (v2)

- Brancher une vraie recherche web (API de recherche) pour couvrir automatiquement LinkedIn/WTTJ/boards africains au lieu de générer seulement des liens.
- Remplacer le CSV de `tracker.py` par Notion/Airtable si tu préfères une vue Kanban.
- Ajouter un scoring pondéré configurable directement dans `criteria.yaml` plutôt que codé en dur dans `scoring.py`.
