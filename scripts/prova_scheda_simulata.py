"""
prova_scheda_simulata.py - una Scheda pezzo di prova con l'AI simulata: gratis, per guardare il frontend.

Testi e foto AI sono finti (le "foto AI" sono la foto stessa); la foto vera ripulita è quella vera,
fatta sul PC. La missione finisce nella cronologia dello Studio come le altre, con "(PROVA)" nel nome.

Uso (dalla cartella del progetto):
    python scripts/prova_scheda_simulata.py                # usa la prima foto in <storage>/input
    python scripts/prova_scheda_simulata.py --foto C:/percorso/foto.jpg
    python scripts/prova_scheda_simulata.py --pulisci      # cancella l'ultima prova e rimette la memoria com'era

ATTENZIONE: lo Studio è collegato al sito vero. Sulla missione di prova NON premere
"Invia bozza" né "Pubblica subito": un pezzo finto finirebbe sul sito.
"""

import argparse
import base64
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
_args = sys.argv[1:]
sys.argv = sys.argv[:1]  # main legge sys.argv all'import
import main  # noqa: E402

PROVE_DIR = main.STORAGE_ROOT / "prove"
MEMORY_BACKUP = PROVE_DIR / "memoria-prima-della-prova"
LAST_RUN = PROVE_DIR / "ultima-prova.json"

ANALISI = """## IDENTIFICAZIONE
- Categoria esatta: Borsa a tracolla artigianale.
- Materiali identificati con certezza: tessuto ricamato.

## DESCRIZIONE AI
Borsa a tracolla in tessuto ricamato a mano, con fiori colorati. Da I Monili Ravenna, via Cavour.
"""
PLAN = {
    "styling": "Con un maglione color panna e jeans dritti, oppure su un vestito lungo a fiori.",
    "woman": "A woman in her late forties, average build, shoulder-length chestnut hair with a few greys, warm smile, linen shirt.",
    "site_prompts": {
        "clean": "The piece on a warm ivory background.",
        "worn": "The piece worn walking in a sunny street of Ravenna.",
    },
}
PACK = {
    "product_name": "Borsa ricamata (PROVA)",
    "seo_title": "Borsa ricamata a mano | I Monili Ravenna",
    "seo_description": "Borsa a tracolla ricamata a mano con fiori colorati. In via Cavour a Ravenna.",
    "whatsapp_share": "Guarda questa borsa ricamata: se ti piace te la mettiamo da parte.",
    "gmb_title": "Nuova borsa ricamata",
    "gmb_text": "Appena arrivata in via Cavour a Ravenna.",
    "caption": "Un giardino da portare a spasso.",
    "hashtags": ["#borsa", "#ricamo", "#artigianale"],
    "cta": "Scrivici in DM, te la mettiamo da parte.",
}


def run(photo: Path) -> None:
    PROVE_DIR.mkdir(parents=True, exist_ok=True)
    if MEMORY_BACKUP.exists():
        shutil.rmtree(MEMORY_BACKUP)
    shutil.copytree(main.MEMORY_ROOT, MEMORY_BACKUP)

    def fake_text(api_key, model, prompt, image_path=None, max_tokens=2048):
        if prompt.startswith("Scrivi i testi della scheda"):
            return json.dumps(PACK)
        if "art director del sito vetrina" in prompt:
            return json.dumps(PLAN)
        return ANALISI

    def fake_image(api_key, model, prompt, image_path=None, aspect_ratio="1:1"):
        return ["data:image/jpeg;base64," + base64.b64encode(photo.read_bytes()).decode("ascii")]

    main.generate_text_with_openrouter = fake_text
    main.generate_image_with_openrouter = fake_image
    before = {p.name for p in main.OUTPUT_ROOT.iterdir()} if main.OUTPUT_ROOT.exists() else set()
    main.run_agency(str(photo), "Prova con AI simulata (PROVA)")
    new = sorted({p.name for p in main.OUTPUT_ROOT.iterdir()} - before - {"reels"})
    LAST_RUN.write_text(json.dumps({"output_dirs": new}, indent=2), encoding="utf-8")
    print(f"\nProva pronta: {new}. Aprila dalla cronologia dello Studio. Per cancellarla: --pulisci")


def clean() -> None:
    if not LAST_RUN.exists():
        print("Nessuna prova da cancellare.")
        return
    for name in json.loads(LAST_RUN.read_text(encoding="utf-8")).get("output_dirs", []):
        target = main.OUTPUT_ROOT / name
        if target.is_dir() and target.parent == main.OUTPUT_ROOT:
            shutil.rmtree(target)
            print(f"Cancellata {name}")
    if MEMORY_BACKUP.exists():
        shutil.rmtree(main.MEMORY_ROOT)
        shutil.copytree(MEMORY_BACKUP, main.MEMORY_ROOT)
        shutil.rmtree(MEMORY_BACKUP)
        print("Memoria rimessa com'era prima della prova.")
    LAST_RUN.unlink()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--foto", type=Path, help="foto del pezzo (default: la prima in <storage>/input)")
    parser.add_argument("--pulisci", action="store_true", help="cancella l'ultima prova e rimette la memoria")
    args = parser.parse_args(_args)
    if args.pulisci:
        clean()
    else:
        inputs = sorted((main.STORAGE_ROOT / "input").glob("*.*"))
        photo = args.foto or (inputs[0] if inputs else None)
        if not photo or not photo.exists():
            sys.exit("Nessuna foto: passa --foto <percorso>")
        run(photo)
