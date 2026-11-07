"""What kind of piece it is, and what follows from it: the shop and the site photos.

Used by the mission (main.py: which photos to make) and by the Studio backend
(api/server.py: the form for sending a piece to the site).
"""
from __future__ import annotations

import re

CATEGORY_WORDS = {
    "abbigliamento": r"giacc|gilet|kimono|cappott|giubb|camici|abit[oi]\b|vestit|magli|cardigan|blus|gonn|pantalon"
    r"|poncho|kaftan|caftan|tunic|felp|trench|blazer|top\b",
    "accessori": r"\bbors|pochette|cintur|foulard|sciarp|cappell|occhial|portafogl|zain|stola|scial",
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
    "Se e un anello (o un bracciale): inquadratura STRETTA, solo il dito con l'anello e le nocche vicine "
    "(la mano e tagliata a meta, mai mano intera ne polso ne braccio); il pezzo occupa almeno un terzo della "
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
