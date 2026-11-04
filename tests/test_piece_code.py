"""Codice breve del pezzo: stesso calcolo del sito (apps/web/src/lib/product-fiche.ts, pieceCode)."""

import re

import main
import piece_code as pc

# Valori di prova condivisi con legal-compliance.test.ts del sito: se cambiano qui, cambiano là.
VECTORS = {
    "20261104_101500_a1b2c3": "M-C8BQK",
    "20261030_183000_7f09de": "M-8QN5G",
    "legal-test": "M-DKX4P",
}


def test_known_values_match_the_site():
    for run_id, code in VECTORS.items():
        assert pc.piece_code(run_id) == code


def test_format_is_short_and_unambiguous():
    for run_id in VECTORS:
        assert pc.CODE_RE.fullmatch(pc.piece_code(run_id))
    assert not re.search(r"[ILOU01]", pc.ALPHABET)
    assert pc.piece_code("") == ""


def test_add_reference_once():
    code = pc.piece_code("legal-test")
    text = pc.add_reference("Anello in argento. Scrivici, ti diciamo se è disponibile.", code)
    assert text.endswith(f"Rif. {code}")
    assert pc.add_reference(text, code) == text


def test_publish_pack_carries_the_code():
    code = pc.piece_code("20261104_101500_a1b2c3")
    pack = main.apply_piece_code(main.normalize_publish_pack({"caption": "Un anello"}), code)
    for key in ("whatsapp_share", "caption", "cta", "selected_caption", "selected_whatsapp"):
        assert code in pack[key]
    assert pack["piece_code"] == code
    assert code in main.format_publish_pack_markdown(pack)
    # Senza codice (run_id mancante) il pacchetto resta com'era.
    assert "Rif." not in main.apply_piece_code(main.normalize_publish_pack({}), "")["caption"]


def test_reel_copy_gets_the_code_only_when_it_comes_from_a_scheda():
    import reel_studio

    code = pc.piece_code("legal-test")
    with_scheda = reel_studio._with_piece_code({"scheda_run_id": "legal-test"}, {"caption": "Ciao", "caption_short": "Ciao"})
    assert with_scheda["caption"].endswith(f"Rif. {code}") and with_scheda["piece_code"] == code
    without = reel_studio._with_piece_code({}, {"caption": "Ciao"})
    assert without == {"caption": "Ciao"}
