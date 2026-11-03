"""Categoria, prezzo e taglia compilati da analisi e descrizione; il negozio lo sceglie sempre chi pubblica."""
import json

import pytest

import api.server as server

# La giacca del 02/11/2026: l'analisi consiglia orecchini e collana da abbinare,
# e prima per questo la giacca finiva tra i Gioielli.
GIACCA = {
    "analisi": (
        "## IDENTIFICAZIONE\n\n### Categoria esatta\n"
        "Giacca corta da donna stile kimono/boho-etnico, aperta sul davanti.\n\n"
        "## STYLING\nCon orecchini pendenti dorati e una collana lunga."
    ),
    "publish_pack_json": json.dumps({"product_name": "Giacca boho lavorata artigianalmente"}),
}


def test_the_jacket_is_clothing_even_if_the_styling_talks_about_earrings():
    assert server._category_for_results(GIACCA, "Giacca lavorata Artigianalmente costo 69€") == "abbigliamento"
    assert not hasattr(server, "SHOP_FOR_CATEGORY")


@pytest.mark.parametrize(
    ("analisi", "category"),
    [
        ("- Categoria esatta: Anello da donna con pietra viola, da portare con un abito lungo.", "gioielli"),
        ("- Categoria esatta: Borsa a spalla in cuoio, perfetta con orecchini grandi.", "accessori"),
        ("- Categoria esatta: Orecchini pendenti a fiore smaltati.", "gioielli"),
    ],
)
def test_the_exact_category_line_wins(analisi, category):
    assert server._category_for_results({"analisi": analisi}) == category


@pytest.mark.parametrize(
    ("brief", "price", "size"),
    [
        ("Giacca lavorata Artigianalmente costo 69€", "69", ""),
        ("Orecchini a fiore 22,50 euro", "22,50", ""),
        ("Anello argento € 35 misura 16", "35", "16"),
        ("Gilet ricamato prezzo: 89 taglia m", "89", "M"),
        ("Borsa in cuoio taglia unica 120€", "120", "Taglia unica"),
        ("Collana lunga con turchese", "", ""),
    ],
)
def test_price_and_size_come_from_the_description(brief, price, size):
    assert server._price_from_brief(brief) == price
    assert server._size_from_brief(brief) == size


def test_candidates_send_the_suggestions_to_the_studio(monkeypatch):
    from fastapi.testclient import TestClient

    payload = {"brief": "Giacca ricamata costo 69€ taglia M", "results": GIACCA}
    monkeypatch.setattr(server, "_find_mission_payload", lambda run_id: payload)
    monkeypatch.setattr(server, "_showcase_image_candidates", lambda results: [])
    data = TestClient(server.app).get("/missions/qualsiasi/showcase/candidates").json()
    # Il negozio non si deduce dalla categoria: lo sceglie chi pubblica.
    assert (data["category"], data["location"], data["price"], data["size"]) == (
        "abbigliamento",
        "",
        "69",
        "M",
    )
