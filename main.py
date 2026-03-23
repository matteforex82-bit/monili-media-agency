"""
main.py — MONILI MEDIA AGENCY
Entry point per la Monili Media Agency AI.
Carica una foto prodotto e genera il kit marketing completo.

Uso:
  python main.py --foto input/orecchini.jpg
  python main.py --foto input/orecchini.jpg --brief "nuovi arrivi, 22€, P/E 2026"
"""
import asyncio
import argparse
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


async def run_agency(foto_path: str, brief: str = "") -> None:
    try:
        from claude_agent_sdk import query, ClaudeAgentOptions
    except ImportError:
        print("❌ claude-agent-sdk non installato. Esegui: pip install -r requirements.txt")
        sys.exit(1)

    foto = Path(foto_path)
    if not foto.exists():
        print(f"❌ Foto non trovata: {foto_path}")
        print("   Metti la foto nella cartella input/ e riprova.")
        sys.exit(1)

    # Crea cartella output con timestamp + nome prodotto
    nome = foto.stem.lower().replace(" ", "-")
    data = datetime.now().strftime("%Y-%m-%d")
    output_dir = Path(f"output/{data}_{nome}")
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n🎬 MONILI MEDIA AGENCY")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"📸 Foto:     {foto_path}")
    print(f"📝 Brief:    {brief or 'auto-analisi'}")
    print(f"📁 Output:   {output_dir}")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    prompt = f"""
Sei la Monili Media Agency. È arrivata una nuova foto prodotto da lavorare.

📸 Foto prodotto: {foto.resolve()}
📝 Brief: {brief if brief else "Nessun brief — analizza il prodotto autonomamente dalla foto"}
📁 Directory output: {output_dir.resolve()}

Esegui il workflow completo in questo ordine:

1. TREND RESEARCH — cerca hashtag virali bijoux/moda Italia OGGI, audio Reels trending, trend P/E 2026
2. PRODUCT ANALYSIS — analizza la foto, classifica il prodotto, produci product_card.md in 01_ANALISI/
3. PHOTOGRAPHY DIRECTION — genera 8-10 prompt shooting (hero, dettaglio, modella, lifestyle, stories), salva in 02_SHOOTING/
4. VISUAL GENERATION — genera le immagini con Gemini/MJ se configurati, altrimenti salva solo i prompt
5. REEL DIRECTION — se il formato è Reel, crea script + frame_prompts.md in 03_REEL/
6. COPY — scrivi 3 varianti caption + stories + WhatsApp + GMB, salva in 04_COPY/copy_completo.md
7. HASHTAG — costruisci set 30 hashtag, salva in 04_COPY/hashtag_30.md
8. FOTO OTTIMIZZATE — esegui scripts/optimize_image.py, salva in 05_FOTO_OTTIMIZZATE/
9. PIANO EDITORIALE — calendario 2 settimane con orari, salva in piano_2settimane.md
10. MEMORY UPDATE — logga questa sessione in memory/performance_log.json

Output directory base: {output_dir.resolve()}
Salva ogni file nella sotto-cartella corretta.
Kit completo pronto per Instagram.
"""

    options = ClaudeAgentOptions(
        cwd=str(Path(".").resolve()),
        setting_sources=["user", "project"],
        allowed_tools=[
            "Skill", "Read", "Write", "Bash",
            "WebSearch", "WebFetch", "Glob", "Grep"
        ]
    )

    print("🚀 Avvio workflow agency...\n")
    async for message in query(prompt=prompt, options=options):
        if hasattr(message, "text") and message.text:
            print(message.text, end="", flush=True)
        elif hasattr(message, "result"):
            print(f"\n\n✅ COMPLETATO!")
            print(f"📁 Output salvato in: {output_dir}")
            print(f"\nFile prodotti:")
            for f in sorted(output_dir.rglob("*")):
                if f.is_file():
                    print(f"   {f.relative_to(output_dir)}")


def main():
    parser = argparse.ArgumentParser(
        description="Monili Media Agency — Kit marketing completo da una foto prodotto"
    )
    parser.add_argument(
        "--foto", "-f",
        default="input/prodotto.jpg",
        help="Path della foto prodotto (default: input/prodotto.jpg)"
    )
    parser.add_argument(
        "--brief", "-b",
        default="",
        help='Brief opzionale (es: "nuovi arrivi P/E, 22€, orecchini estivi")'
    )
    args = parser.parse_args()
    asyncio.run(run_agency(args.foto, args.brief))


if __name__ == "__main__":
    main()
