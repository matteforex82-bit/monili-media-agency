"""Codice breve del pezzo (es. «M-7K2QD»): lo stesso su scheda del sito, caption, WhatsApp e Reel.

Si ricava dal `run_id` della Scheda pezzo, che esiste fin dall'inizio: nessun archivio da tenere.
Il sito (`pieceCode` in apps/web/src/lib/product-fiche.ts) usa lo stesso calcolo sul `sourceRunId`:
i due test (tests/test_piece_code.py e legal-compliance.test.ts) condividono gli stessi valori di prova.
Alfabeto senza I, L, O, U e senza 0/1, per non confondere le lettere quando il codice si detta o si scrive.
"""

from __future__ import annotations

import re

ALPHABET = "23456789ABCDEFGHJKMNPQRSTVWXYZ"
PREFIX = "M-"
LENGTH = 5
CODE_RE = re.compile(r"\bM-[2-9A-HJKMNP-TV-Z]{5}\b")


def piece_code(run_id: str) -> str:
    """Codice del pezzo dal run_id della Scheda; stringa vuota se manca il run_id."""
    value = (run_id or "").strip()
    if not value:
        return ""
    h = 0x811C9DC5  # FNV-1a a 32 bit
    for byte in value.encode("utf-8"):
        h = ((h ^ byte) * 0x01000193) & 0xFFFFFFFF
    chars = []
    for _ in range(LENGTH):
        chars.append(ALPHABET[h % len(ALPHABET)])
        h //= len(ALPHABET)
    return PREFIX + "".join(chars)


def add_reference(text: str, code: str) -> str:
    """Aggiunge «Rif. M-XXXXX» in fondo al testo, una sola volta."""
    text = (text or "").strip()
    if not code or code in text:
        return text
    return f"{text} Rif. {code}".strip()
