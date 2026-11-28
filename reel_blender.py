"""Pianificazione Reel Blender. La produzione video rimane una fase separata."""

import json
from pathlib import Path

from pydantic import BaseModel, Field, StringConstraints
from typing import Annotated, Literal

import fucina_codex
import prompt_lab
from main import BRAND, extract_json_object

ShortText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)]
LongText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=3500)]
ProductName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
Template = Literal[
    "Outfit completo", "Giacca o gilet", "Anello", "Orecchini", "Bracciale", "Collana", "Borsa", "Cintura",
    "Capo singolo", "Cavigliera", "Pochette", "Sciarpa, stola o scialle", "Foulard o bandana", "Cappello",
    "Regia libera",
]
DIRECTION_GUIDE = Path(__file__).resolve().parent / "knowledge" / "reel-blender-regia.md"
PRODUCT_TEMPLATES = DIRECTION_GUIDE.with_name("reel-blender-template-prodotti.md")


class Concept(BaseModel):
    title: ShortText
    hook: ShortText
    sequence: ShortText
    risk: ShortText


class PieceRecognition(BaseModel):
    product: ProductName
    template: Template
    detail: ShortText


class PieceQuestion(BaseModel):
    clarification: ShortText


class Concepts(BaseModel):
    concepts: list[Concept] = Field(min_length=3, max_length=3)
    recommended: int = Field(ge=0, le=2)
    recommendation_reason: ShortText | None = None
    recognition: PieceRecognition | None = None


class ShotDesign(BaseModel):
    purpose: ShortText
    scale: Literal["look", "medium", "detail", "macro"]
    reference_photo: int = Field(default=1, ge=1, le=3)
    focus_x: float = Field(default=0.5, ge=0, le=1)
    focus_y: float = Field(default=0.5, ge=0, le=1)
    lens_mm: int = Field(default=50, ge=28, le=120)
    yaw_deg: int = Field(default=0, ge=-35, le=35)
    pitch_deg: int = Field(default=0, ge=-20, le=20)
    stage_action: Literal["rest", "reveal", "handle", "worn", "turn"] | None = None
    motion: Literal["fixed", "push", "slide", "orbit"] = "fixed"
    light: Literal["soft", "texture", "jewelry"] = "soft"
    key_side: Literal["left", "front", "right"] = "left"
    sound: ShortText
    accent: Literal["none", "soft", "strong"] = "none"


class Direction(BaseModel):
    set_mood: Literal["warm_cream", "deep_charcoal", "neutral"] = "warm_cream"
    set_design: ShortText
    continuity: ShortText
    music_bpm: int = Field(default=100, ge=72, le=130)
    music_feel: ShortText


class Shot(BaseModel):
    end_ms: int = Field(gt=0)
    framing: ShortText
    camera: ShortText
    lighting: ShortText
    action: ShortText
    cut: ShortText
    design: ShotDesign
    photo_prompt_en: LongText | None = None
    video_prompt_en: LongText | None = None


class Handoff(BaseModel):
    storyboard: LongText
    assets: LongText
    audio: LongText
    blender: LongText
    higgsfield: LongText
    pilot_shot_index: int | None = Field(default=None, ge=0, lt=6)
    direction: Direction
    shots: list[Shot] = Field(min_length=3, max_length=6)


def product_title(draft: dict) -> str:
    return draft.get("product") or (draft.get("recognition") or {}).get("product") or "Reel dalla foto"


def _templates_for(template: str | None) -> str:
    catalog = PRODUCT_TEMPLATES.read_text(encoding="utf-8")
    if not template or template == "Regia libera":
        return catalog
    intro, common, *sections = catalog.split("\n## ")
    selected = next((section for section in sections if section.splitlines()[0] == template), None)
    return "\n## ".join((intro, common, selected)) if selected else catalog


def _ask(draft: dict, instructions: str, images: list[Path], recognition: dict | None = None) -> dict:
    brief = {key: draft[key] for key in ("product", "brief", "target_seconds")}
    if recognition:
        brief["product"] = product_title(draft)
        brief["riconoscimento"] = recognition
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

GUIDA DI REGIA FASHION, BIJOUX E MONTAGGIO
{DIRECTION_GUIDE.read_text(encoding="utf-8")}

TEMPLATE DI REGIA PER TIPO DI PRODOTTO
Scegli la scheda del protagonista dal nome dichiarato o dalle foto quando il nome è vuoto. Se il brief include un riconoscimento, usa quella scheda e il suo dettaglio visivo.
Usa Outfit completo se il protagonista è l'insieme. Mantieni la scheda del protagonista quando compaiono accessori di styling.
Ricava dalla scheda cosa far capire del pezzo e cosa controllare. Crea la sequenza sulle caratteristiche documentate di questo pezzo.
Tratta ordine, campi, angoli, movimenti e timecode della scheda come esempi. Adattali all'idea, alle viste disponibili e alla musica.
Usa la stessa scheda per concept e shot list. Spiega in assets le sole foto utili a questo Reel.
{_templates_for((recognition or {}).get("template"))}

BRIEF
{json.dumps(brief, ensure_ascii=False)}

{instructions}

Rispondi con un solo oggetto JSON."""
    return extract_json_object(fucina_codex.run(prompt, images))


def generate_concepts(draft: dict, images: list[Path]) -> dict:
    result = _ask(draft, """Se ci sono foto, identifica il protagonista e il dettaglio visibile che dà un motivo all'apertura.
Se il nome è dichiarato, usalo per distinguere il protagonista dagli accessori. Se il nome è vuoto e due prodotti sono
ugualmente protagonisti, o il pezzo non è riconoscibile, restituisci solo {"clarification":"una domanda breve con le alternative visibili, se ci sono"}.
Se il protagonista è chiaro, compila recognition con un nome breve, il titolo esatto di una scheda del catalogo (oppure Regia libera)
e un dettaglio verificabile a vista. Usa descrizioni visive. Evita di dedurre materiale, marca, misure o vestibilità non mostrati.
Valuta tre concept con aperture distinte e una progressione visiva diversa per ciascuno.
Per ogni concept abbina l'apertura a una caratteristica documentata o a una domanda sul pezzo, come forma, scala o texture.
Scegli tu l'idea più forte per questo prodotto. Dai priorità a un elemento riconoscibile nel primo secondo, a una rivelazione
leggibile subito dopo e a una ripresa fattibile che conservi il pezzo. Il Reel deve avere senso anche senza musica.
Spiega la scelta in una frase concreta legata alle foto e alla tenuta dell'attenzione. Evita promesse di viralità.
Schema: {"concepts":[{"title":"...", "hook":"...", "sequence":"...", "risk":"..."}], "recommended":0,
"recommendation_reason":"...", "recognition":{"product":"Giacca ricamata", "template":"Giacca o gilet", "detail":"Motivo ricamato sulle maniche"}}
recommended è l'indice 0, 1 o 2 del concept che hai scelto. Ometti recognition se lavori senza foto.""", images)
    if not images:
        result.pop("recognition", None)
    if not draft["product"] and result.get("clarification"):
        question = PieceQuestion.model_validate(result)
        return {"concepts": [], "clarification": question.clarification}
    concepts = Concepts.model_validate(result)
    if not draft["product"] and concepts.recognition is None:
        return {"concepts": [], "clarification": "Quale pezzo vuoi mettere al centro del Reel?"}
    return concepts.model_dump(exclude_none=True)


def generate_handoff(draft: dict, images: list[Path], index: int) -> dict:
    selected = draft["concepts"][index]
    duration_ms = draft["target_seconds"] * 1000
    result = _ask(draft, f"""Sviluppa solo il concept scelto: {json.dumps(selected, ensure_ascii=False)}
Rendi leggibile il gancio visivo nel primo secondo. Nel montaggio, punta a 0,8–1,5 secondi per l'apertura
e mostra il pezzo in contesto entro circa 3 secondi. Se la proposta di concept indica un'apertura più lunga,
accorciala e ridistribuisci il tempo per far leggere il prodotto. Puoi generare una clip sorgente più lunga e rifilarla.
Indica quali foto usare, scattare o generare e quando girare una clip reale. Includi ritmo, marker audio e musica guida.
Nel piano di montaggio indica i tagli, dove tenere lo spazio per la grafica e quando far entrare la scritta in Remotion.
Prevedi un file sorgente per inquadratura, anche da foto reale o ripresa reale quando è la fonte più fedele.
Non dare per certi materiali o caratteristiche che dalle foto e dal brief non si possono verificare.
Per Blender indica camera per shot, posa e riferimenti. Per Higgsfield scegli una sola ripresa da verificare per prima.
Indica pilot_shot_index (indice dello shot a partire da 0) e spiega in higgsfield perché questa ripresa è utile e cosa controllare.
Preferisci uno shot che permetta di giudicare insieme fedeltà del prodotto, posa e movimento previsto. Usa Seedance con riferimenti.
Compila direction e design per ogni shot: sono i comandi che la scena Blender legge, oltre alle note per il montatore.
focus_x e focus_y sono il centro d'interesse sulla foto (origine in alto a sinistra, 0–1); reference_photo è l'indice 1–3.
Usa scale look/medium/detail/macro; motion fixed/push/slide/orbit; luce soft/texture/jewelry; key_side left/front/right.
lens_mm 28–120, yaw_deg -35–35, pitch_deg -20–20.
Blender costruisce per ogni inquadratura una scena 3D stilizzata adatta al tipo di accessorio (banco del negozio, scrigno, mano, busto,
manichino) e ci muove la camera: non usa le foto, che servono solo a te. Scegli per ogni shot stage_action, cosa succede nella scena:
rest (il pezzo è fermo sul banco o sul manichino), reveal (lo scrigno si apre sul pezzo, per i gioielli piccoli), handle (una mano
arriva, prende il pezzo e lo solleva), worn (il pezzo è indossato e la camera gira intorno), turn (il pezzo o il manichino ruota piano).
Per un gioiello piccolo apri con reveal o rest in macro, usa handle a metà e chiudi con worn. Per un capo o una borsa su manichino usa turn e worn.
Una scena dentro un portico o una strada non serve: il pezzo sta sul suo banco, non nel quartiere.
Usa set_mood warm_cream/deep_charcoal/neutral, BPM 72–130. accent fa risuonare none/soft/strong all'inizio dello shot.
Specifica il perché di ogni inquadratura, il punto d'interesse e il raccordo col prossimo taglio. Scegli pochi accenti, anche solo quello della rivelazione.
Scrivi due prompt specifici in inglese per ogni ripresa. photo_prompt_en prepara il primo fotogramma, con posa, crop e luce.
video_prompt_en descrive una sola azione e il movimento, con indicazioni di fedeltà al pezzo e senza audio generato.
Schema: {{"storyboard":"...", "assets":"...", "audio":"...", "blender":"...", "higgsfield":"...", "pilot_shot_index":1,
"direction":{{"set_mood":"warm_cream","set_design":"...","continuity":"...","music_bpm":96,"music_feel":"..."}},
"shots":[{{"end_ms":1200, "framing":"...", "camera":"...", "lighting":"...", "action":"...", "cut":"...",
"design":{{"purpose":"...", "scale":"macro", "reference_photo":1, "focus_x":0.5, "focus_y":0.5,
"lens_mm":85, "yaw_deg":0, "pitch_deg":0, "motion":"push", "light":"texture",
"key_side":"left", "stage_action":"reveal", "sound":"...", "accent":"none"}}, "photo_prompt_en":"...", "video_prompt_en":"..."}}]}}
Servono 3-6 shot. end_ms è il tempo assoluto di fine in millisecondi, strettamente crescente, a partire da 0.
L'ultimo end_ms è esattamente {duration_ms}.""", images, recognition=draft.get("recognition"))
    package = Handoff.model_validate(result).model_dump(exclude_none=True)
    ends = [shot["end_ms"] for shot in package["shots"]]
    if ends != sorted(set(ends)) or ends[-1] != duration_ms:
        raise ValueError("I tempi delle inquadrature non coprono la durata del Reel.")
    if package.get("pilot_shot_index", 0) >= len(ends):
        package.pop("pilot_shot_index")
    return package


def format_time(milliseconds: int) -> str:
    minutes, remainder = divmod(milliseconds, 60_000)
    seconds, fraction = divmod(remainder, 1000)
    return f"{minutes:02}:{seconds:02}.{fraction:03}"


def markdown(draft: dict) -> str:
    package = draft["package"]
    concept = draft["concepts"][draft["selected"]]
    sections = [
        f"# {product_title(draft)} · Reel Blender",
        f"Formato 9:16 · {draft['target_seconds']} s",
        f"## Brief\n\n{draft['brief'] or 'Brief libero.'}",
        f"## Concept scelto\n\n**{concept['title']}**\n\n{concept['hook']}\n\n{concept['sequence']}",
    ]
    for key, title in (
        ("storyboard", "Storyboard"), ("assets", "Foto e riprese"), ("audio", "Musica e montaggio"),
        ("blender", "Scheda per Claude e Blender"), ("higgsfield", "Prova Higgsfield"),
    ):
        sections.append(f"## {title}\n\n{package[key]}")
    direction = package.get("direction")
    if direction:
        sections.append(f"## Scenografia e continuità\n\n{direction['set_design']}\n\n{direction['continuity']}")
        sections.append(f"## Traccia guida\n\n{direction['music_bpm']} BPM · {direction['music_feel']}")
    sections.append("## Shot list")
    start = 0
    for shot in package["shots"]:
        end = shot["end_ms"]
        sections.append(
            f"### {format_time(start)}–{format_time(end)} · {shot['framing']}\n\n"
            f"- Camera — {shot['camera']}\n- Luce — {shot['lighting']}\n"
            f"- Azione — {shot['action']}\n- Taglio — {shot['cut']}"
        )
        design = shot.get("design")
        if design:
            sections[-1] += (
                f"\n- Funzione — {design['purpose']}\n- Suono — {design['sound']}"
                f"\n- Blender — {design['lens_mm']} mm, foto {design['reference_photo']}"
            )
        start = end
    return "\n\n".join(sections) + "\n"
