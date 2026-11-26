"""Pianificazione Reel Blender. La produzione video rimane una fase separata."""

import json
from pathlib import Path

from pydantic import BaseModel, Field, StringConstraints
from typing import Annotated

import prompt_lab
from main import BRAND, extract_json_object, generate_text_with_openrouter, select_openrouter_text_model

ShortText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)]
LongText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=3500)]


class Concept(BaseModel):
    title: ShortText
    hook: ShortText
    sequence: ShortText
    risk: ShortText


class Concepts(BaseModel):
    concepts: list[Concept] = Field(min_length=3, max_length=3)
    recommended: int = Field(ge=0, le=2)
    recommendation_reason: ShortText | None = None


class Shot(BaseModel):
    end_ms: int = Field(gt=0)
    framing: ShortText
    camera: ShortText
    lighting: ShortText
    action: ShortText
    cut: ShortText


class Handoff(BaseModel):
    storyboard: LongText
    assets: LongText
    audio: LongText
    blender: LongText
    higgsfield: LongText
    shots: list[Shot] = Field(min_length=3, max_length=6)


def _ask(draft: dict, api_key: str, instructions: str, images: list[Path], max_tokens: int) -> dict:
    brief = {key: draft[key] for key in ("product", "brief", "target_seconds")}
    if draft.get("photos"):
        brief["foto_in_ordine"] = [photo["filename"] for photo in draft["photos"]]
    source = (
        "Usa tutte le foto reali allegate per controllare i dettagli visibili. Se serve, fai riferimento al numero della foto nell’ordine degli allegati."
        if images else "Pianifica da testo: indica cosa confermare sulle foto, senza inventare caratteristiche del pezzo."
    )
    prompt = f"""Sei il regista Reel Blender di I Monili Ravenna. Scrivi in italiano; eventuali prompt per generatori video vanno in inglese.
Progetta riprese originali 9:16. Preferisci una modella già in posa, gesti brevi e un cambio di scala o camera motivato.
{source}

BRAND
{BRAND}

REGIA VIDEO
{prompt_lab.video_direction()}

BRIEF
{json.dumps(brief, ensure_ascii=False)}

{instructions}

Rispondi con un solo oggetto JSON."""
    return extract_json_object(generate_text_with_openrouter(
        api_key, select_openrouter_text_model(), prompt, image_path=images or None, max_tokens=max_tokens, all_images=True,
    ))


def generate_concepts(draft: dict, api_key: str, images: list[Path]) -> dict:
    result = _ask(draft, api_key, """Valuta tre concept con aperture distinte e scegli tu quello con il miglior potenziale per questo pezzo.
Dai priorità a un dettaglio reale che cattura lo sguardo nel primo secondo, a una rivelazione leggibile subito dopo
e a una ripresa fattibile che conservi il prodotto. Il Reel deve avere senso anche senza musica.
Spiega la scelta in una frase concreta legata alle foto e alla tenuta dell'attenzione. Evita promesse di viralità.
Schema: {"concepts":[{"title":"...", "hook":"...", "sequence":"...", "risk":"..."}], "recommended":0,
"recommendation_reason":"..."}
recommended è l'indice 0, 1 o 2 del concept che hai scelto.""", images, 3000)
    return Concepts.model_validate(result).model_dump(exclude_none=True)


def generate_handoff(draft: dict, api_key: str, images: list[Path], index: int) -> dict:
    selected = draft["concepts"][index]
    duration_ms = draft["target_seconds"] * 1000
    result = _ask(draft, api_key, f"""Sviluppa solo il concept scelto: {json.dumps(selected, ensure_ascii=False)}
Rendi leggibile il gancio visivo nel primo secondo. Nel montaggio, punta a 0,8–1,5 secondi per l'apertura
e mostra il pezzo in contesto entro circa 3 secondi. Se la proposta di concept indica un'apertura più lunga,
accorciala e ridistribuisci il tempo per far leggere il prodotto. Puoi generare una clip sorgente più lunga e rifilarla.
Indica quali foto usare, scattare o generare e quando girare una clip reale. Includi ritmo, marker audio e musica guida.
Non dare per certi materiali o caratteristiche che dalle foto e dal brief non si possono verificare.
Per Blender indica formato, camera per shot, pose e segnaposto. Per Higgsfield descrivi il test su un solo shot e i controlli di fedeltà.
Schema: {{"storyboard":"...", "assets":"...", "audio":"...", "blender":"...", "higgsfield":"...",
"shots":[{{"end_ms":1200, "framing":"...", "camera":"...", "lighting":"...", "action":"...", "cut":"..."}}]}}
Servono 3-6 shot. end_ms è il tempo assoluto di fine in millisecondi, strettamente crescente, a partire da 0.
L'ultimo end_ms è esattamente {duration_ms}.""", images, 5200)
    package = Handoff.model_validate(result).model_dump()
    ends = [shot["end_ms"] for shot in package["shots"]]
    if ends != sorted(set(ends)) or ends[-1] != duration_ms:
        raise ValueError("I tempi delle inquadrature non coprono la durata del Reel.")
    return package


def format_time(milliseconds: int) -> str:
    minutes, remainder = divmod(milliseconds, 60_000)
    seconds, fraction = divmod(remainder, 1000)
    return f"{minutes:02}:{seconds:02}.{fraction:03}"


def markdown(draft: dict) -> str:
    package = draft["package"]
    concept = draft["concepts"][draft["selected"]]
    sections = [
        f"# {draft['product']} · Reel Blender",
        f"Formato 9:16 · {draft['target_seconds']} s",
        f"## Brief\n\n{draft['brief'] or 'Brief libero.'}",
        f"## Concept scelto\n\n**{concept['title']}**\n\n{concept['hook']}\n\n{concept['sequence']}",
    ]
    for key, title in (
        ("storyboard", "Storyboard"), ("assets", "Foto e riprese"), ("audio", "Musica e montaggio"),
        ("blender", "Scheda per Claude e Blender"), ("higgsfield", "Prova Higgsfield"),
    ):
        sections.append(f"## {title}\n\n{package[key]}")
    sections.append("## Shot list")
    start = 0
    for shot in package["shots"]:
        end = shot["end_ms"]
        sections.append(
            f"### {format_time(start)}–{format_time(end)} · {shot['framing']}\n\n"
            f"- Camera — {shot['camera']}\n- Luce — {shot['lighting']}\n"
            f"- Azione — {shot['action']}\n- Taglio — {shot['cut']}"
        )
        start = end
    return "\n\n".join(sections) + "\n"
