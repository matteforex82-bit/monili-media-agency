"""What kind of piece it is, and what follows from it: the shop and the site photos.

Used by the mission (main.py: which photos to make) and by the Studio backend
(api/server.py: the form for sending a piece to the site).
"""
from __future__ import annotations

import re

CATEGORY_WORDS = {
    "abbigliamento": r"giacc|gilet|kimono|cappott|giubb|camici|abit[oi]\b|vestit|magli|cardigan|blus|gonn|pantalon"
    r"|poncho|kaftan|caftan|tunic|felp|trench|blazer|top\b",
    "accessori": r"\bbors|pochette|cintur|foulard|sciarp|cappell|portafogl|zain|stola|scial",
    "gioielli": r"collan|braccial|anell|orecchin|cavigliera|ciondol|spilla|gioiell|parure",
}

LABELS = {"abbigliamento": "Abbigliamento", "accessori": "Accessori", "gioielli": "Gioielli", "bijoux": "Bijoux"}

# The shop is never worked out from the category (PRD Journey cliente, 03/11/2026):
# silver and stones are at no. 17, the rest at no. 21, but only the owner knows where
# the real piece is, so the Studio always asks.

# The site photos follow what makes a customer write (Matteo, 02/11/2026). The
# cover is always the real photo cleaned on the PC; the AI only shows the piece
# worn. For clothing the question is "how does it fit?": two worn shots. For
# jewelry and accessories it is the stone, the leather, the clasp: one worn
# shot and the real detail photo, when one is uploaded.
AI_SHOTS = {
    "abbigliamento": ["worn", "worn_2"],
    "gioielli": ["worn"],
    "bijoux": ["worn"],
    "accessori": ["worn"],
}

# Rings and bracelets: Matteo does not want the whole hand (07/11/2026), only a part of it with the
# piece worn and a lovely blurred background.
RING_FRAMING = (
    "Se e un anello: inquadratura STRETTA, solo il dito con l'anello e le nocche vicine "
    "(la mano e tagliata a meta, mai mano intera ne polso ne braccio). Se e un bracciale: primo piano su polso e "
    "avambraccio, mano rilassata e tagliata. In entrambi i casi il pezzo occupa almeno un terzo della "
    "larghezza; sfondo bello ma sfocato (muro caldo, mosaico, tessuto), mai neutro e vuoto."
)

# How the art director frames the worn shots, per category (Italian, it goes in the prompt).
SHOT_GUIDE = {
    "abbigliamento": (
        'CAPO DI ABBIGLIAMENTO. "worn": figura intera, di fronte, si vedono bene vestibilita, lunghezza e come cade. '
        '"worn_2": un altro angolo e un altro abbinamento (tre quarti, di schiena o mentre cammina), stessa donna, '
        "luogo diverso dal primo."
    ),
    "gioielli": (
        'GIOIELLO. "worn": primo piano sulla parte del corpo giusta (orecchio, mano, collo o polso), il pezzo grande '
        "nell'inquadratura e nitido, si capiscono misura e colore della pietra. " + RING_FRAMING
    ),
    "bijoux": (
        'BIJOU. "worn": primo piano sulla parte del corpo giusta (orecchio, mano, collo o polso), il pezzo grande '
        "nell'inquadratura e nitido, si capiscono misura e colori. " + RING_FRAMING
    ),
    "accessori": (
        'ACCESSORIO. "worn": a mezzo busto, la donna lo porta (borsa in spalla o a mano, foulard al collo, cintura in '
        "vita): si capisce quanto e grande rispetto al corpo."
    ),
}


# What kind of jewel / garment / accessory it is (PRD prompt completi, 20/11/2026). Each type has its review sheet
# (knowledge/valutazione/valutazione-<sheet>.md), its framing (knowledge/fucina/inquadratura-tipi.md, section "## <tipo>")
# and the share of the 4:5 frame the cut-out piece fills on the site's base photo, so two pieces of the same type
# come out at the same scale.
SUBTYPE_WORDS = {
    "anello": r"anell",
    "orecchini": r"orecchin",
    "collana": r"collan|ciondol|girocoll",
    "bracciale": r"braccial",
    "cavigliera": r"cavigli",
    "pochette": r"pochette|clutch",
    "borsa": r"\bbors|zain|portafogl|tracoll",
    "sciarpa": r"sciarp|stola|scial",
    "foulard": r"foulard|bandana",
    "cintura": r"cintur",
    "cappello": r"cappell|basco|berretto",
}

SUBTYPES = {
    #  tipo          categoria        etichetta       parte del corpo per la foto indossata      riempimento base
    "anello": {"category": "bijoux", "label": "Anello", "body": "dito e nocche", "fill": 0.55},
    "orecchini": {"category": "bijoux", "label": "Orecchini", "body": "orecchio e linea della mascella", "fill": 0.62},
    "collana": {"category": "bijoux", "label": "Collana", "body": "collo e scollatura", "fill": 0.72},
    "bracciale": {"category": "bijoux", "label": "Bracciale", "body": "polso e avambraccio", "fill": 0.62},
    "cavigliera": {"category": "bijoux", "label": "Cavigliera", "body": "caviglia nuda e piede", "fill": 0.66},
    "borsa": {"category": "accessori", "label": "Borsa", "body": "fianco e busto (piano americano)", "fill": 0.78},
    "pochette": {"category": "accessori", "label": "Pochette", "body": "mano e busto", "fill": 0.72},
    "sciarpa": {"category": "accessori", "label": "Sciarpa", "body": "collo, spalle e busto", "fill": 0.80},
    "foulard": {"category": "accessori", "label": "Foulard", "body": "collo e spalle", "fill": 0.74},
    "cintura": {"category": "accessori", "label": "Cintura", "body": "vita e fianchi", "fill": 0.80},
    "cappello": {"category": "accessori", "label": "Cappello", "body": "testa e viso", "fill": 0.70},
    "capo": {"category": "abbigliamento", "label": "Capo di abbigliamento", "body": "figura (vedi taglio)", "fill": 0.80},
}

# Clothing: the cut changes the worn framing (top: half figure; bottom: from the waist down; whole: full figure).
GARMENT_CUTS = {
    "sopra": r"giacc|gilet|kimono|camici|magli|cardigan|blus|\btop\b|felp|blazer|poncho|tunic|giubb|bolero",
    "sotto": r"gonn|pantalon|\bshort|jeans",
    "intero": r"abit[oi]\b|vestit|kaftan|caftan|cappott|trench|tuta|chemisier",
}
CUT_LABELS = {"sopra": "sopra (busto)", "sotto": "sotto (gambe)", "intero": "figura intera"}


def _first_match(patterns: dict[str, str], *sources: str) -> str:
    for text in sources:
        lowered = (text or "").lower()
        found = [(m.start(), name) for name, pattern in patterns.items() if (m := re.search(pattern, lowered))]
        if found:
            return min(found)[1]
    return ""


def subtype_from(*sources: str, category: str = "") -> str:
    """The kind of piece (a key of SUBTYPES): the first product word found, sources in order of reliability.
    Clothing is always "capo" (the cut is a separate field); nothing found: the category's generic type."""
    if category == "abbigliamento":
        return "capo"
    found = _first_match(SUBTYPE_WORDS, *sources)
    if found:
        return found
    return {"abbigliamento": "capo", "accessori": "foulard"}.get(category, "")


def subtype_for(category: str, *sources: str) -> str:
    """Like subtype_from, but only the types of this category count (the analysis also names what to pair it with:
    "con una borsa in cuoio" must not turn a ring into a bag). Nothing found: the category's generic type."""
    if category == "abbigliamento":
        return "capo"
    wanted = recipe_category(category)
    patterns = {name: pattern for name, pattern in SUBTYPE_WORDS.items() if SUBTYPES[name]["category"] == wanted}
    return _first_match(patterns, *sources) or {"accessori": "foulard"}.get(wanted, "")


def garment_cut(*sources: str) -> str:
    """sopra, sotto or intero for a garment; intero when nothing says otherwise."""
    return _first_match(GARMENT_CUTS, *sources) or "intero"


def valid_subtype(value: object) -> str:
    text = str(value or "").strip().lower()
    return text if text in SUBTYPES else ""


def valid_cut(value: object) -> str:
    text = str(value or "").strip().lower()
    return text if text in GARMENT_CUTS else ""


def recipe_category(category: str) -> str:
    """The name of the recipe file (knowledge/fucina/ricetta-<x>.md): the mission says "gioielli", the recipe is "bijoux"."""
    return "bijoux" if category in ("gioielli", "bijoux", "") else category


FILL_BY_TYPE = False  # da tarare con Matteo: con i valori della tabella i gioielli venivano più piccoli (prova 20/11)


def subtype_fill(subtype: str) -> float | None:
    """Share of the frame per type. Off for now: the old fixed fill already gives every piece the same scale."""
    return (SUBTYPES.get(subtype) or {}).get("fill") if FILL_BY_TYPE else None


def category_in(text: str) -> str | None:
    """The category of the first product word in the text (the item named first)."""
    lowered = text.lower()
    found = [
        (match.start(), category)
        for category, pattern in CATEGORY_WORDS.items()
        if (match := re.search(pattern, lowered))
    ]
    return min(found)[1] if found else None


def exact_category_line(analisi: str) -> str:
    match = re.search(r"categoria esatta[*:\s]*(?:[-*]\s*)?(.+)", analisi, flags=re.IGNORECASE)
    return match.group(1) if match else ""


def category_from(analisi: str, product_name: str = "", brief: str = "", extra: str = "") -> str:
    """The analysis also suggests what to pair the piece with ("con orecchini..."):
    the category comes from what the piece is, read in order of reliability."""
    for source in (exact_category_line(analisi), product_name, brief, extra or analisi):
        category = category_in(source)
        if category:
            return category
    return "bijoux"