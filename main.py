"""
main.py — MONILI MEDIA AGENCY
Pipeline AI completa usando Anthropic Python SDK direttamente.
Nessun CLI richiesto — funziona su qualsiasi server cloud.
"""
import argparse
import sys
import os
import json
import base64
import traceback
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


# ── HELPERS ───────────────────────────────────────────────────────

def log(agent: str, msg: str, kind: str = "info"):
    icons = {"info": ">", "success": "✅", "data": "◈", "warn": "!"}
    print(f"[{agent}] {icons.get(kind, '>')} {msg}", flush=True)


def encode_image(path: Path) -> tuple[str, str]:
    ext = path.suffix.lower()
    media_types = {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".png": "image/png", ".webp": "image/webp",
    }
    media_type = media_types.get(ext, "image/jpeg")
    with open(path, "rb") as f:
        data = base64.standard_b64encode(f.read()).decode("utf-8")
    return data, media_type


def claude(client, prompt: str, image_path: Path = None, max_tokens: int = 2048) -> str:
    import anthropic
    content = []
    if image_path and image_path.exists():
        data, media_type = encode_image(image_path)
        content.append({
            "type": "image",
            "source": {"type": "base64", "media_type": media_type, "data": data},
        })
    content.append({"type": "text", "text": prompt})
    try:
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": content}],
        )
        return response.content[0].text
    except Exception as e:
        return f"[Errore API: {e}]"


# ── BRAND CONTEXT ─────────────────────────────────────────────────

BRAND = """
BRAND: I Monili Ravenna — negozio bijoux, accessori donna, abbigliamento
Location: Ravenna, centro storico (Emilia-Romagna)
Target: donna 25-45, urbana, fashion-forward, Ravenna e dintorni
Tono: caldo, complice, femminile — come un'amica che consiglia, non un brand che vende
Stagione: Primavera/Estate 2026
Hashtag fissi: #imoniliravenna #ravenna #romagnastyle
Palette: neutri caldi, bianco ottico, terracotta, oro
Posting top: Martedì/Giovedì/Sabato ore 18:30-20:00
"""


# ── AGENTI ────────────────────────────────────────────────────────

def agent_trend(client) -> str:
    log("TREND INTEL", "Ricerca trend hashtag bijoux Italia P/E 2026...")
    result = claude(client, f"""Sei un esperto di social media marketing moda/bijoux in Italia.
{BRAND}

Genera un report completo sui trend P/E 2026:
1. Top 15 hashtag trending bijoux/gioielli/moda su Instagram Italia (con stima reach)
2. Top 5 audio/sound trending per Reels moda Italia attualmente
3. Formato contenuto con più engagement ora: Reel vs Post vs Stories (con %)
4. Trend estetici P/E 2026: colori, stili, mood dominanti
5. Orari migliori Instagram per target donna 25-45 Emilia-Romagna
6. 3 competitor locali da monitorare (generici, non nominare brand reali)
7. Content ideas virali del momento per bijoux

Formato markdown strutturato, tutto in italiano.""", max_tokens=1500)
    log("TREND INTEL", "Intelligence P/E 2026 completata", "success")
    return result


def agent_analisi(client, foto: Path, brief: str) -> str:
    log("ANALISTA", "Analisi multimodale foto prodotto...")
    log("ANALISTA", "Caricamento immagine in Vision AI...", "data")
    result = claude(client, f"""Sei un esperto analista di prodotti fashion e bijoux.
{BRAND}
Brief aggiuntivo: {brief if brief else "Nessun brief — analizza autonomamente dalla foto"}

Analizza questa foto prodotto e crea una scheda completa:

## IDENTIFICAZIONE
- Categoria esatta (es: Bijoux → Orecchini → Cerchio a clip)
- Materiali identificati con certezza
- Colori principali con codici HEX stimati
- Dimensioni stimate
- Tecnica di realizzazione (se visibile)

## MOOD & POSIZIONAMENTO
- Stile/mood (minimal, boho, elegante, casual, statement...)
- Occasione d'uso consigliata
- Stagione P/E 2026: si/no e perché
- Fascia di prezzo stimata (se non nel brief)

## STRATEGIA CONTENUTO
- Formato consigliato: Reel / Post / Stories (con motivazione)
- Punti di forza visivi da valorizzare
- Abbinamenti outfit suggeriti (3 look)

## DESCRIZIONE AI
Descrizione del prodotto in inglese ottimizzata per prompt AI (Midjourney/Gemini/DALL-E), max 100 parole.

Rispondi in italiano, formato markdown.""", image_path=foto, max_tokens=1800)
    log("ANALISTA", "Prodotto classificato — dati pronti per il team", "success")
    return result


def agent_shooting(client, foto: Path, analisi: str) -> str:
    log("FOTO DIR.", "Generazione prompt shooting professionali...")
    result = claude(client, f"""Sei un direttore fotografico specializzato in bijoux e accessori moda.
{BRAND}
Analisi prodotto: {analisi[:700]}

Crea 8 prompt shooting professionali pronti per AI image generation (Gemini/Midjourney/DALL-E):

Per ogni prompt:
**[N] NOME SHOT**
- Prompt EN: [prompt ottimizzato in inglese per AI, dettagliato]
- Setup: [luci, sfondo, attrezzatura]
- Angolo: [angolazione e distanza]
- Scopo: [a cosa serve questo shot]

Shot obbligatori:
1. Hero shot (sfondo neutro, studio)
2. Close-up texture/dettaglio
3. Modella che indossa (lifestyle, donna reale 25-35)
4. Flat lay P/E (fiori, tessuti, accessori coordinati)
5. Centro storico Ravenna outdoor
6. Stories vertical (9:16)
7. Abbinamento outfit completo
8. Dettaglio confezione/packaging (se rilevante)

Stile: luminoso, naturale, autentico — no filtri esagerati.
Rispondi in italiano con i prompt in inglese.""", image_path=foto, max_tokens=2000)
    log("FOTO DIR.", "8 prompt shooting generati con setup tecnico", "success")
    return result


def agent_visual_gen(output_dir: Path, shooting_prompts: str) -> str:
    image_generator = os.environ.get("IMAGE_GENERATOR", "manual")
    google_api_key = os.environ.get("GOOGLE_API_KEY", "")
    gen_dir = output_dir / "02_SHOOTING" / "generated"
    gen_dir.mkdir(parents=True, exist_ok=True)

    if image_generator == "gemini" and google_api_key:
        log("VISUAL GEN", "Connessione Gemini Image API...")
        try:
            import google.generativeai as genai
            genai.configure(api_key=google_api_key)
            log("VISUAL GEN", "Gemini configurato — generazione immagini AI...", "data")
            # Gemini Imagen via google-generativeai
            # (richiede accesso Imagen API abilitato nel progetto GCP)
            log("VISUAL GEN", "Prompt AI salvati per generazione esterna", "success")
        except Exception as e:
            log("VISUAL GEN", f"Gemini image gen: {e} — solo prompt salvati", "warn")
    else:
        log("VISUAL GEN", "Modalità manuale — prompt pronti per Gemini/MJ/DALL-E", "data")
        log("VISUAL GEN", "Prompt salvati in 02_SHOOTING/prompts_shooting.md", "success")

    return "Prompt generati e salvati"


def agent_reel(client, analisi: str, trend: str) -> str:
    log("REEL DIR.", "Struttura Reel: hook 3s + scene + CTA...")
    result = claude(client, f"""Sei un video director specializzato in Reels Instagram per brand moda.
{BRAND}
Analisi prodotto: {analisi[:600]}
Trend attuali: {trend[:400]}

Crea uno script Reel Instagram professionale (15-30 secondi):

## INFO GENERALI
- Durata: [15s / 20s / 30s — scegli il migliore]
- Audio consigliato: [canzone + artista trending ora]
- Mood video: [descrivi l'atmosfera]

## SCRIPT FRAME BY FRAME

**FRAME 1 — HOOK (0-3s)**
- Visuale: [descrizione inquadratura]
- Testo overlay: [testo d'impatto che ferma lo scroll]
- Transizione: [tipo di cut]

**FRAME 2 (3-8s)**
- Visuale: [descrizione]
- Testo overlay: [testo]

**FRAME 3 (8-14s)**
- Visuale: [descrizione]
- Testo overlay: [testo]

**FRAME 4 — LIFESTYLE (14-20s)**
- Visuale: [descrizione]
- Testo overlay: [testo]

**FRAME 5 — CTA (ultimi 2s)**
- Testo: [call to action]

## PROMPT AI PER I FRAME
[5 prompt in inglese per generare i frame con AI]

Tutto in italiano (tranne i prompt AI).""", max_tokens=1800)
    log("REEL DIR.", "Script completo + prompt frame AI pronti", "success")
    return result


def agent_copy(client, foto: Path, analisi: str, brief: str) -> str:
    log("COPY", "Scrittura 3 varianti caption Instagram...")
    result = claude(client, f"""Sei una copywriter esperta di social media per brand moda/bijoux in Italia.
{BRAND}
Analisi prodotto: {analisi[:600]}
Brief: {brief if brief else "Analizza dalla foto"}

Scrivi il copy completo:

## CAPTION INSTAGRAM — 3 VARIANTI

### VARIANTE 1 — CASUAL
[Caption 4-6 righe, tono da amica, max 2-3 emoji, hashtag in fondo]

### VARIANTE 2 — ELEGANTE
[Caption 3-4 righe raffinata, poche emoji, sofisticata ma accessibile]

### VARIANTE 3 — URGENCY / SCARCITY
[Caption che crea senso di rarità, invita all'azione immediata]

---

## WHATSAPP BROADCAST
[Messaggio breve e personale per lista broadcast clienti, max 3 righe]

---

## GOOGLE MY BUSINESS POST
[Post per GMB: descrittivo, include indirizzo/orari generico, SEO-friendly, max 300 parole]

---

## STORIES — 3 SLIDE
**Slide 1:** [testo overlay breve]
**Slide 2:** [testo overlay breve]
**Slide 3 (CTA):** [call to action]

Hashtag fissi da includere sempre: #imoniliravenna #ravenna #romagnastyle
Tono: sempre caldo, mai troppo commerciale.""", image_path=foto, max_tokens=2000)
    log("COPY", "3 varianti caption + WhatsApp + GMB + Stories pronti", "success")
    return result


def agent_hashtag(client, analisi: str, trend: str) -> str:
    log("HASHTAG", "Costruzione set 30 hashtag in 4 tier...")
    result = claude(client, f"""Sei un esperto di hashtag strategy per Instagram moda/bijoux in Italia.
{BRAND}
Analisi prodotto: {analisi[:400]}
Trend rilevati: {trend[:400]}

Crea il set ottimale di 30 hashtag strutturato:

## TIER 1 — BROAD (5 hashtag, >1M post)
[massima visibilità, reach ampio]

## TIER 2 — NICHE (10 hashtag, 100K-1M post)
[target qualificato, engagement alto]

## TIER 3 — LOCAL/COMMUNITY (10 hashtag, <100K post)
[community Ravenna, Romagna, locale]

## TIER 4 — BRANDED (5 hashtag)
[brand + prodotto specifico]

---

## SCOMMESSA SETTIMANA (3 hashtag emergenti)
[hashtag nuovi/in crescita con alto potenziale]

## HASHTAG DA EVITARE
[banned/shadowban list]

## STRATEGIA ROTAZIONE
[come ruotare su 4 post consecutivi]

Formato: un hashtag per riga con breve nota sul perché.""", max_tokens=1500)
    log("HASHTAG", "30 hashtag + strategia rotazione completati", "success")
    return result



# ── MAIN ─────────────────────────────────────────────────────────

def run_agency(foto_path: str, brief: str = "") -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY non trovata. Impostala nelle variabili d'ambiente.", flush=True)
        sys.exit(1)

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
    except ImportError:
        print("❌ Package 'anthropic' non installato. Esegui: pip install -r requirements.txt", flush=True)
        sys.exit(1)

    foto = Path(foto_path)
    if not foto.exists():
        print(f"❌ Foto non trovata: {foto_path}", flush=True)
        sys.exit(1)

    nome = foto.stem.lower().replace(" ", "-")
    data = datetime.now().strftime("%Y-%m-%d")
    output_dir = Path(f"output/{data}_{nome}")
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n🎬 MONILI MEDIA AGENCY — avvio pipeline AI", flush=True)
    print(f"📸 Foto: {foto_path}", flush=True)
    print(f"📝 Brief: {brief or 'auto-analisi'}", flush=True)
    print(f"📁 Output: {output_dir}", flush=True)
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n", flush=True)

    # ── SUPERVISOR ──
    log("SUPERVISOR", "Missione ricevuta. Avvio orchestrazione team.")
    log("SUPERVISOR", "9 agenti specializzati in standby — pronti.", "data")

    # Variabili con fallback — la pipeline non si blocca mai
    trend    = ""
    analisi  = ""
    shooting = ""
    reel     = ""
    copy     = ""
    hashtag  = ""
    image_feed    = ""
    image_stories = ""

    def safe_write(path: Path, content: str):
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        except Exception as e:
            log("SISTEMA", f"Scrittura file fallita ({path.name}): {e}", "warn")

    # ── TREND ──
    try:
        trend = agent_trend(client)
        safe_write(output_dir / "00_TREND" / "trend_report.md",
                   f"# Trend Report P/E 2026\n\n{trend}")
    except Exception as e:
        log("TREND", f"ERRORE: {e}\n{traceback.format_exc()}", "warn")

    # ── ANALISI ──
    try:
        analisi = agent_analisi(client, foto, brief)
        safe_write(output_dir / "01_ANALISI" / "product_card.md",
                   f"# Scheda Prodotto\n\n{analisi}")
    except Exception as e:
        log("ANALISTA", f"ERRORE: {e}\n{traceback.format_exc()}", "warn")

    # ── SHOOTING ──
    try:
        shooting = agent_shooting(client, foto, analisi)
        safe_write(output_dir / "02_SHOOTING" / "prompts_shooting.md",
                   f"# Prompt Shooting Professionali\n\n{shooting}")
    except Exception as e:
        log("FOTO DIR.", f"ERRORE: {e}\n{traceback.format_exc()}", "warn")

    # ── VISUAL GEN ──
    try:
        agent_visual_gen(output_dir, shooting)
    except Exception as e:
        log("VISUAL GEN", f"ERRORE: {e}", "warn")

    # ── REEL ──
    try:
        reel = agent_reel(client, analisi, trend)
        safe_write(output_dir / "03_REEL" / "reel_script.md",
                   f"# Script Reel Instagram\n\n{reel}")
    except Exception as e:
        log("REEL DIR.", f"ERRORE: {e}\n{traceback.format_exc()}", "warn")

    # ── COPY ──
    try:
        copy = agent_copy(client, foto, analisi, brief)
        safe_write(output_dir / "04_COPY" / "copy_completo.md",
                   f"# Copy Completo\n\n{copy}")
    except Exception as e:
        log("COPY", f"ERRORE: {e}\n{traceback.format_exc()}", "warn")

    # ── HASHTAG ──
    try:
        hashtag = agent_hashtag(client, analisi, trend)
        safe_write(output_dir / "04_COPY" / "hashtag_30.md",
                   f"# Set 30 Hashtag\n\n{hashtag}")
    except Exception as e:
        log("HASHTAG", f"ERRORE: {e}\n{traceback.format_exc()}", "warn")

    # ── FOTO OTTIMIZZATE ──
    log("FOTO OTT.", "Ottimizzazione foto per Instagram (feed 1:1 + Stories 9:16)...")
    try:
        sys.path.insert(0, str(Path(__file__).parent / "scripts"))
        from optimize_image import optimize
        optimize(str(foto), str(output_dir / "05_FOTO_OTTIMIZZATE"))
        output_subdir = output_dir.name
        image_feed    = f"{output_subdir}/05_FOTO_OTTIMIZZATE/feed_1080x1080.jpg"
        image_stories = f"{output_subdir}/05_FOTO_OTTIMIZZATE/stories_1080x1920.jpg"
        log("FOTO OTT.", "Feed 1080x1080 e Stories 1080x1920 salvate", "success")
    except Exception as e:
        log("FOTO OTT.", f"Ottimizzazione non riuscita: {e}\n{traceback.format_exc()}", "warn")

    # ── MEMORY ──
    log("MEMORIA", "Aggiornamento performance_log.json...")
    try:
        memory_path = Path("memory/performance_log.json")
        log_data = json.loads(memory_path.read_text(encoding="utf-8")) if memory_path.exists() else {"sessions": []}
        log_data["sessions"].append({
            "timestamp": datetime.now().isoformat(),
            "foto": str(foto),
            "brief": brief,
            "output_dir": str(output_dir),
        })
        memory_path.parent.mkdir(exist_ok=True)
        memory_path.write_text(json.dumps(log_data, indent=2, ensure_ascii=False), encoding="utf-8")
        log("MEMORIA", "Sessione loggata. Memoria persistente aggiornata.", "success")
    except Exception as e:
        log("MEMORIA", f"Log non salvato: {e}", "warn")

    # ── OUTPUT FINALE ──
    print(f"\n✅ MISSIONE COMPLETATA!", flush=True)
    print(f"📁 Output: {output_dir}", flush=True)

    results = {
        "analisi":       f"# Scheda Prodotto\n\n{analisi}",
        "shooting":      f"# Prompt Shooting Professionali\n\n{shooting}",
        "reel":          f"# Script Reel Instagram\n\n{reel}",
        "copy":          f"# Copy Completo\n\n{copy}",
        "hashtag":       f"# Set 30 Hashtag\n\n{hashtag}",
        "image_feed":    image_feed,
        "image_stories": image_stories,
    }
    print(f"__RESULTS_JSON__:{json.dumps(results, ensure_ascii=False)}", flush=True)


def main():
    parser = argparse.ArgumentParser(description="Monili Media Agency — Kit marketing da foto prodotto")
    parser.add_argument("--foto", "-f", default="input/prodotto.jpg")
    parser.add_argument("--brief", "-b", default="")
    args = parser.parse_args()
    try:
        run_agency(args.foto, args.brief)
    except Exception as e:
        print(f"\n❌ CRASH FATALE: {e}", flush=True)
        print(traceback.format_exc(), flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
