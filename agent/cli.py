"""Point d'entrée CLI de l'agent MCPS Job Agent.

Usage:
    python -m agent.cli discover [--query ...] [--limit N] [--min-score N] [--save]
    python -m agent.cli draft --job-file FILE --out-dir DIR [--lang fr|en] ...
    python -m agent.cli track add|update|report ...
"""
import argparse
import json
from datetime import datetime
from pathlib import Path

import yaml
from dotenv import load_dotenv

from agent import generator, scoring, tracker
from agent.search_builder import build_search_plan
from agent.sources import arbeitnow, remoteok, remotive

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"

load_dotenv()


def load_yaml(name: str) -> dict:
    with open(CONFIG_DIR / name, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_text(name: str) -> str:
    with open(CONFIG_DIR / name, encoding="utf-8") as f:
        return f.read()


def cmd_discover(args: argparse.Namespace) -> None:
    criteria = load_yaml("criteria.yaml")
    profile = load_yaml("profile.yaml")

    sources_cfg = criteria.get("sources", {})
    all_jobs = []
    if sources_cfg.get("remotive", True):
        all_jobs += remotive.fetch(args.query)
    if sources_cfg.get("remoteok", True):
        all_jobs += remoteok.fetch(args.query)
    if sources_cfg.get("arbeitnow", True):
        all_jobs += arbeitnow.fetch(args.query)

    scored = [(*scoring.score_job(job, criteria), job) for job in all_jobs]
    scored.sort(key=lambda x: x[0], reverse=True)

    print(f"\n{len(scored)} offre(s) trouvée(s) via APIs publiques pour '{args.query}'\n")
    shown = 0
    for s, reasons, job in scored:
        if s < args.min_score:
            continue
        if shown >= args.limit:
            break
        shown += 1
        print(f"[{s:>3}] {job['title']} — {job['company']} ({job.get('location', '?')}) [{job['source']}]")
        print(f"      {job['url']}")
        for r in reasons:
            print(f"      · {r}")
        print()

    if shown == 0:
        print("Aucune offre au-dessus du seuil min-score sur les APIs publiques — "
              "compte surtout sur la recherche manuelle ci-dessous pour l'Afrique "
              "francophone et l'Europe francophone, mal couvertes par ces APIs.\n")

    if args.save:
        out_dir = Path("data/discovered")
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{datetime.now():%Y%m%d_%H%M%S}.json"
        with out_path.open("w", encoding="utf-8") as f:
            json.dump([job for _, _, job in scored], f, ensure_ascii=False, indent=2)
        print(f"Résultats bruts sauvegardés dans {out_path}\n")

    print("--- Recherche manuelle complémentaire (LinkedIn, WTTJ, boards Afrique, etc.) ---")
    for item in build_search_plan(profile, criteria):
        print(f"- [{item['platform']}] {item['note']}\n  {item['url']}")


def cmd_draft(args: argparse.Namespace) -> None:
    profile = load_yaml("profile.yaml")
    region_norms = load_text("region_norms.md")
    mcps = load_text("mcps_methodology.md")

    job_text = Path(args.job_file).read_text(encoding="utf-8")
    job = {
        "title": args.title or "Directeur Créatif",
        "company": args.company or "Entreprise cible",
        "location": args.location or "",
        "description": job_text,
    }

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Génération du CV...")
    cv = generator.draft_cv(profile, job, region_norms, mcps, lang=args.lang)
    (out_dir / f"CV_{args.lang}.md").write_text(cv, encoding="utf-8")

    print("Génération de la lettre de motivation...")
    letter = generator.draft_cover_letter(profile, job, region_norms, mcps, lang=args.lang)
    (out_dir / f"Lettre_{args.lang}.md").write_text(letter, encoding="utf-8")

    print(f"\nCV et lettre générés dans {out_dir}/")


def cmd_track_add(args: argparse.Namespace) -> None:
    tracker.add_entry({
        "company": args.company,
        "title": args.title,
        "region": args.region or "",
        "source": args.source or "",
        "url": args.url or "",
        "score": args.score or "",
        "status": args.status or "à postuler",
        "next_action": args.next_action or "",
        "notes": args.notes or "",
    })
    print("Candidature ajoutée au pipeline.")


def cmd_track_update(args: argparse.Namespace) -> None:
    tracker.update_status(args.company, args.title, args.status, args.next_action or "")
    print("Statut mis à jour.")


def cmd_track_report(_args: argparse.Namespace) -> None:
    print(tracker.report())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mcps-agent", description="Agent de recherche de poste Directeur Créatif")
    sub = parser.add_subparsers(dest="command", required=True)

    p_discover = sub.add_parser("discover", help="Chercher des offres via APIs publiques + liens de recherche manuelle")
    p_discover.add_argument("--query", default="creative director")
    p_discover.add_argument("--limit", type=int, default=20)
    p_discover.add_argument("--min-score", type=int, default=0)
    p_discover.add_argument("--save", action="store_true")
    p_discover.set_defaults(func=cmd_discover)

    p_draft = sub.add_parser("draft", help="Générer un CV et une lettre de motivation adaptés à une offre")
    p_draft.add_argument("--job-file", required=True, help="Fichier texte contenant le texte de l'offre")
    p_draft.add_argument("--title")
    p_draft.add_argument("--company")
    p_draft.add_argument("--location")
    p_draft.add_argument("--lang", choices=["fr", "en"], default="fr")
    p_draft.add_argument("--out-dir", required=True)
    p_draft.set_defaults(func=cmd_draft)

    p_track = sub.add_parser("track", help="Suivre le pipeline de candidatures")
    track_sub = p_track.add_subparsers(dest="track_command", required=True)

    p_track_add = track_sub.add_parser("add")
    p_track_add.add_argument("--company", required=True)
    p_track_add.add_argument("--title", required=True)
    p_track_add.add_argument("--region")
    p_track_add.add_argument("--source")
    p_track_add.add_argument("--url")
    p_track_add.add_argument("--score")
    p_track_add.add_argument("--status")
    p_track_add.add_argument("--next-action")
    p_track_add.add_argument("--notes")
    p_track_add.set_defaults(func=cmd_track_add)

    p_track_update = track_sub.add_parser("update")
    p_track_update.add_argument("--company", required=True)
    p_track_update.add_argument("--title", required=True)
    p_track_update.add_argument("--status", required=True)
    p_track_update.add_argument("--next-action")
    p_track_update.set_defaults(func=cmd_track_update)

    p_track_report = track_sub.add_parser("report")
    p_track_report.set_defaults(func=cmd_track_report)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
