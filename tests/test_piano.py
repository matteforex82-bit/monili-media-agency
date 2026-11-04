"""Piano editoriale: le regole del perimetro (docs/piano-editoriale-studio.md), senza rete e senza chiavi."""
import json
from datetime import date, timedelta

import pytest

import piano
import skills_loader

CAL = piano.load_calendar()
TODAY = date(2026, 11, 4)  # mercoledi'; settimana dal 2 novembre


def make_catalog(count: int = 10, with_extra: bool = True) -> list[dict]:
    titles = [
        "Anello in argento con ametista", "Orecchini smaltati a fiore", "Collana con quarzo rosa",
        "Bracciale in argento", "Borsa in cuoio", "Orecchini pendenti turchese", "Anello con citrino",
        "Gilet ricamato", "Cavigliera in argento", "Pochette boho", "Anello con opale", "Collana lunga",
    ]
    rows = []
    for i in range(count):
        rows.append(
            {
                "run_id": f"20261{i % 3}01_10{i:02d}00_a1b2{i:02d}",
                "product_id": f"pezzo-{i}",
                "title": titles[i % len(titles)],
                "price": [29, 39, 45, 65, 85, 120][i % 6],
                "category": "bijoux",
                "location": "via-cavour-17" if i % 2 == 0 else "via-cavour-21",
                "state": "unique",
                "published": True,
                "published_at": f"2026-10-{30 - i:02d}T10:00:00",
                "cover": f"{i}/cover.jpg",
            }
        )
    if with_extra:  # pezzi che NON devono mai essere proposti
        base = dict(rows[0], published_at="2026-10-31T10:00:00")
        rows += [
            dict(base, run_id="bozza-1", published=False),
            dict(base, run_id="senza-prezzo", price=None),
            dict(base, run_id="senza-foto", cover=""),
            dict(base, run_id="venduto", state="sold"),
        ]
    return rows


def weeks_from(start: date, count: int, catalog=None, state=None, refiner=None):
    state = state if state is not None else piano.empty_state()
    catalog = catalog if catalog is not None else make_catalog()
    out = []
    for index in range(count):
        monday = start + timedelta(days=7 * index)
        piano.ensure_week(state, monday, catalog, CAL, refiner)
        out.append(monday)
    return state, out


def proposals(state, monday):
    return {role: state["settimane"][monday.isoformat()][role]["proposta"] for role in piano.ROLES}


def test_calendar_only_uses_real_skills():
    available = {s["id"] for s in skills_loader.list_skills()}
    used = set(CAL["note_skill"])
    for role in CAL["ruoli"].values():
        used |= set(role["skills"])
    for event in CAL["eventi"]:
        for cfg in event["ruoli"].values():
            used |= set(cfg.get("skills", []))
    assert used <= available


def test_two_proposals_a_week_with_skill_piece_reason_and_brief():
    state, (monday,) = weeks_from(piano.monday_of(TODAY), 1)
    found = proposals(state, monday)
    assert set(found) == {"scoperta", "acquisto"}
    for proposal in found.values():
        assert proposal["skill"]["id"] and proposal["motivo"] and proposal["brief"]
        piece = proposal["pezzo"]
        assert piece["code"].startswith("M-") and piece["price_text"].endswith("€") and piece["cover"]
        assert piece["location_label"].startswith("via Cavour")
        assert proposal["storie_promemoria"]


def test_only_published_pieces_with_price_and_photo():
    catalog = make_catalog()
    allowed = {p["run_id"] for p in piano.eligible_pieces(catalog)}
    assert not allowed & {"bozza-1", "senza-prezzo", "senza-foto", "venduto"}
    state, weeks = weeks_from(date(2026, 11, 2), 12, catalog)
    for monday in weeks:
        for proposal in proposals(state, monday).values():
            assert proposal["pezzo"]["run_id"] in allowed


def test_never_the_same_skill_two_weeks_in_a_row_nor_twice_in_a_week():
    state, weeks = weeks_from(date(2026, 10, 26), 12)
    for index, monday in enumerate(weeks):
        today = {p["skill"]["id"] for p in proposals(state, monday).values()}
        assert len(today) == 2
        if index:
            before = {p["skill"]["id"] for p in proposals(state, weeks[index - 1]).values()}
            assert not today & before, (monday, today, before)


def test_no_piece_repeated_within_three_weeks_and_two_pieces_per_week_differ():
    state, weeks = weeks_from(date(2026, 10, 26), 12)
    seen = []  # (indice settimana, run_id)
    for index, monday in enumerate(weeks):
        runs = [p["pezzo"]["run_id"] for p in proposals(state, monday).values()]
        assert len(set(runs)) == 2
        seen += [(index, r) for r in runs]
    for i, (wi, run) in enumerate(seen):
        for wj, other in seen[i + 1:]:
            if other == run:
                assert wj - wi >= piano.MIN_WEEKS_BETWEEN_SAME_PIECE


def test_the_two_shops_alternate():
    state, weeks = weeks_from(date(2026, 10, 26), 8)
    mixed = 0
    for monday in weeks:
        locations = {p["pezzo"]["location"] for p in proposals(state, monday).values()}
        mixed += len(locations) == 2
    assert mixed >= len(weeks) - 1  # con due negozi disponibili quasi ogni settimana li usa entrambi


def test_every_brief_has_closing_price_and_code_and_nothing_promised():
    state, weeks = weeks_from(date(2026, 10, 26), 12)
    for monday in weeks:
        for proposal in proposals(state, monday).values():
            brief = proposal["brief"]
            assert piano.CLOSING in brief
            assert proposal["pezzo"]["price_text"] in brief and proposal["pezzo"]["code"] in brief
            for field in ("brief", "storie", "storie_promemoria"):
                assert not piano.WEEKDAY_RE.search(proposal[field]), field
                assert not piano.DATE_RE.search(proposal[field]), field
            assert not piano.validate_brief(brief, proposal["pezzo"], True)


def test_black_friday_week_has_no_promotional_words():
    friday_week = date(2026, 11, 23)  # la settimana del 27/11
    assert piano.event_for_week(CAL, friday_week)["no_promo"] is True
    catalog = make_catalog()
    for changes in range(6):
        state = piano.empty_state()
        piano.ensure_week(state, friday_week, catalog, CAL)
        for role in piano.ROLES:
            for _ in range(changes):
                piano.altra_idea(state, friday_week, role, catalog, CAL)
            proposal = state["settimane"][friday_week.isoformat()][role]["proposta"]
            text = " ".join([proposal["brief"], proposal["storie"], proposal["tema"]])
            assert not piano.PROMO_RE.search(text), text
    for event in CAL["eventi"]:  # nessun evento del calendario promette sconti
        assert event["no_promo"] is True


def test_another_idea_really_changes_and_never_returns_to_discarded_ones():
    catalog = make_catalog()
    state, (monday,) = weeks_from(date(2026, 11, 2), 1, catalog)
    first = proposals(state, monday)["acquisto"]
    seen = {(first["skill"]["id"], first["pezzo"]["run_id"])}
    for _ in range(4):
        new = piano.altra_idea(state, monday, "acquisto", catalog, CAL)["proposta"]
        key = (new["skill"]["id"], new["pezzo"]["run_id"])
        assert key not in seen
        seen.add(key)
        # le regole valgono anche dopo il cambio
        other = proposals(state, monday)["scoperta"]
        assert new["skill"]["id"] != other["skill"]["id"] and new["pezzo"]["run_id"] != other["pezzo"]["run_id"]


def test_skipping_is_recorded_and_the_slot_is_not_proposed_again_that_week():
    catalog = make_catalog()
    state, (monday,) = weeks_from(date(2026, 11, 2), 1, catalog)
    piano.salta(state, monday, "scoperta", "x" * 500)
    slot = state["settimane"][monday.isoformat()]["scoperta"]
    assert slot["stato"] == "saltato" and len(slot["motivo_salto"]) == piano.MAX_SKIP_NOTE
    before = json.dumps(slot, sort_keys=True)
    piano.ensure_week(state, monday, catalog, CAL)
    view = piano.build_view(state, catalog, CAL, TODAY)
    assert json.dumps(state["settimane"][monday.isoformat()]["scoperta"], sort_keys=True) == before
    assert view["settimane"][0]["slot"]["scoperta"]["stato"] == "saltato"
    with pytest.raises(piano.PianoError):
        piano.altra_idea(state, monday, "scoperta", catalog, CAL)


def test_created_published_and_provisional_weeks():
    catalog = make_catalog()
    state = piano.empty_state()
    view = piano.build_view(state, catalog, CAL, TODAY)
    assert [w["provvisoria"] for w in view["settimane"]] == [False, True, True]
    assert view["settimane"][0]["corrente"] and view["settimane"][0]["inizio"] == "2026-11-02"
    assert list(state["settimane"]) == ["2026-11-02"]  # le anteprime non si salvano
    monday = date(2026, 11, 2)
    assert piano.collega_reel(state, f"{monday}:acquisto", "reel-1", TODAY)
    assert state["settimane"]["2026-11-02"]["acquisto"]["stato"] == "creato"
    piano.segna_pubblicato(state, monday, "acquisto", TODAY)
    assert state["settimane"]["2026-11-02"]["acquisto"]["pubblicato_il"] == "2026-11-04"
    with pytest.raises(piano.PianoError):  # le anteprime non si modificano
        piano.salta(state, date(2026, 11, 9), "scoperta")
    # le anteprime rispettano le stesse regole rispetto alla settimana corrente
    skills_now = {p["skill"]["id"] for p in proposals(state, monday).values()}
    next_skills = {s["proposta"]["skill"]["id"] for s in view["settimane"][1]["slot"].values()}
    assert not skills_now & next_skills


def test_without_pieces_or_ai_the_plan_still_works_and_heals():
    state = piano.empty_state()
    view = piano.build_view(state, [], CAL, TODAY)
    for slot in view["settimane"][0]["slot"].values():
        assert slot["proposta"]["pezzo"] is None and slot["proposta"]["avvisi"]
        assert piano.CLOSING in slot["proposta"]["brief"]
    view = piano.build_view(state, make_catalog(), CAL, TODAY)  # appena c'e' un pezzo, la proposta si aggiorna
    assert all(s["proposta"]["pezzo"] for s in view["settimane"][0]["slot"].values())


def test_a_sold_piece_is_replaced_before_it_is_created():
    catalog = make_catalog()
    state, (monday,) = weeks_from(date(2026, 11, 2), 1, catalog)
    chosen = proposals(state, monday)["acquisto"]["pezzo"]["run_id"]
    sold = [dict(p, state="sold") if p["run_id"] == chosen else p for p in catalog]
    piano.ensure_week(state, monday, sold, CAL)
    assert proposals(state, monday)["acquisto"]["pezzo"]["run_id"] != chosen


def test_price_band_only_when_there_is_a_fitting_piece():
    gift_week = date(2026, 11, 16)
    state = piano.empty_state()
    piano.ensure_week(state, gift_week, make_catalog(), CAL)
    gift = proposals(state, gift_week)["acquisto"]
    assert gift["pezzo"]["price"] <= 50 and "sotto i 50" in gift["brief"]
    expensive = [dict(p, price=120) for p in make_catalog()]
    state = piano.empty_state()
    piano.ensure_week(state, gift_week, expensive, CAL)
    assert "sotto i 50" not in proposals(state, gift_week)["acquisto"]["brief"]


def test_ai_rewrite_is_used_only_if_it_passes_the_same_checks():
    catalog = make_catalog()

    def good(brief, ctx):
        return brief + " Tono caldo."

    def bad_promo(brief, ctx):
        return brief + " Con uno sconto del 20%."

    def bad_missing(brief, ctx):
        return "Un bel contenuto."

    def boom(brief, ctx):
        raise RuntimeError("rete")

    for refiner, used in ((good, True), (bad_promo, False), (bad_missing, False), (boom, False)):
        state, (monday,) = weeks_from(date(2026, 11, 23), 1, catalog, refiner=refiner)
        proposal = proposals(state, monday)["acquisto"]
        assert proposal["brief_ai"] is used
        assert not piano.validate_brief(proposal["brief"], proposal["pezzo"], True)


def test_state_file_has_no_customer_data_and_roundtrips(tmp_path):
    state, _ = weeks_from(date(2026, 11, 2), 2)
    path = tmp_path / "piano.json"
    piano.save_state(state, path)
    assert piano.load_state(path) == json.loads(path.read_text(encoding="utf-8"))
    text = path.read_text(encoding="utf-8").lower()
    for forbidden in ("telefono", "cliente", "whatsapp", "@", "indirizzo"):
        assert forbidden not in text
    assert piano.load_state(tmp_path / "manca.json") == piano.empty_state()
