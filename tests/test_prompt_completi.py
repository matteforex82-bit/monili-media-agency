"""PRD prompt completi (20/11/2026): ogni tipo di prodotto ha scheda, inquadratura, scala e knowledge nei prompt
finali (foto sito, scene video, storyboard, post con testo, testi). Senza rete e senza chiavi."""
import base64
import io
import json

import pytest
from fastapi.testclient import TestClient
from PIL import Image

import api.server as server
import categorie
import main
import photo_cleanup
import post_grafica
import prompt_lab
import reel_studio

client = TestClient(server.app)
MAX_PROMPT_WORDS = 9000  # la knowledge entra intera nei prompt: un tetto per accorgersi se cresce troppo
MISSION_CATEGORY = {"bijoux": "gioielli", "accessori": "accessori", "abbigliamento": "abbigliamento"}


def _png(color=(200, 180, 150), size=(1200, 1500)) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", size, color).save(buffer, "PNG")
    return buffer.getvalue()


# -- T1 / T2: tipi, schede, inquadrature -----------------------------------------------------------------------
@pytest.mark.parametrize("subtype", sorted(categorie.SUBTYPES))
def test_every_type_has_its_sheet_framing_and_scale(subtype):
    spec = categorie.SUBTYPES[subtype]
    assert spec["category"] in prompt_lab.CATEGORIES
    assert prompt_lab.review_sheet(subtype, "clean") and prompt_lab.review_sheet(subtype, "worn"), subtype
    cuts = list(categorie.GARMENT_CUTS) if subtype == "capo" else [""]
    for cut in cuts:
        assert prompt_lab.type_guide(subtype, cut), (subtype, cut)
    assert 0.4 < spec["fill"] < 0.95


def test_a_type_without_its_sheet_would_be_caught(monkeypatch):
    monkeypatch.setitem(categorie.SUBTYPES, "spilla", {"category": "bijoux", "label": "Spilla", "body": "petto", "fill": 0.6})
    assert not prompt_lab.review_sheet("spilla", "worn") and not prompt_lab.type_guide("spilla")


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("cavigliera in argento con ciondoli", "cavigliera"),
        ("braccialetto con turchese", "bracciale"),
        ("pochette ricamata con perline", "pochette"),
        ("borsa a spalla in cuoio", "borsa"),
        ("sciarpa in lana a righe", "sciarpa"),
        ("foulard di seta stampato", "foulard"),
        ("cintura in cuoio con fibbia", "cintura"),
        ("cappello di paglia a tesa larga", "cappello"),
        ("occhiali da sole tartarugati", "occhiali"),
    ],
)
def test_each_new_type_is_recognised_on_its_own(text, expected):
    assert categorie.subtype_from(text) == expected


def test_the_type_stays_inside_the_category_and_clothing_has_a_cut():
    # the analysis suggests what to pair the piece with: a ring stays a ring
    assert categorie.subtype_for("gioielli", "", "Anello con ametista, da portare con una borsa in cuoio") == "anello"
    assert categorie.subtype_for("accessori", "nulla di preciso") == "foulard"
    assert categorie.garment_cut("Gonna lunga a balze") == "sotto"
    assert categorie.garment_cut("Gilet ricamato") == "sopra"
    assert categorie.garment_cut("qualcosa") == "intero"
    assert categorie.recipe_category("gioielli") == "bijoux"


# -- il bug della missione: la ricetta dei gioielli non arrivava ----------------------------------------------
def test_the_mission_category_and_the_real_model_id_reach_the_knowledge():
    text = prompt_lab.model_knowledge("openai/gpt-image-2.6-sunburst", "gioielli")
    assert "Conoscenza: GPT Image" in text and "Ricetta: bijoux" in text
    assert "Conoscenza: Nano Banana" in prompt_lab.model_knowledge("google/gemini-nano-banana-2.1")


@pytest.mark.parametrize("subtype", sorted(categorie.SUBTYPES))
def test_the_site_plan_prompt_has_recipe_model_type_and_rules(subtype, monkeypatch, tmp_path):
    seen = []
    monkeypatch.setattr(main, "generate_text_with_openrouter", lambda *a, **k: seen.append(a[2]) or "{}")
    category = MISSION_CATEGORY[categorie.SUBTYPES[subtype]["category"]]
    cut = "sotto" if subtype == "capo" else ""
    main.agent_scheda_plan("m", "k", tmp_path / "x.jpg", "analisi", "", category, main.DEFAULT_OPENROUTER_IMAGE_MODEL, subtype, cut)
    prompt = seen[0]
    recipe = categorie.recipe_category(category)
    assert f"Ricetta: {recipe}" in prompt
    assert "Conoscenza: Nano Banana" in prompt  # il modello immagini di default della missione
    assert "Struttura del prompt per le foto" in prompt
    assert prompt_lab.type_guide(subtype, cut) in prompt
    assert "COSE DA NON MOSTRARE MAI" in prompt
    assert len(prompt.split()) < MAX_PROMPT_WORDS


def test_the_mission_uses_the_chosen_type_its_scale_and_the_testimonial_photos(monkeypatch, tmp_path):
    import casting

    prompts, images, cleans = [], [], []

    def fake_text(api_key, model, prompt, image_path=None, max_tokens=2048):
        prompts.append(prompt)
        if "art director del sito" in prompt:
            return json.dumps({"styling": "s", "woman": "w", "site_prompts": {"clean": "c", "worn": "anklet on a bare ankle"}})
        return "## IDENTIFICAZIONE\n- Categoria esatta: bracciale in argento"

    def fake_image(api_key, model, prompt, image_path=None, aspect_ratio="1:1"):
        images.append((prompt, image_path))
        return ["data:image/png;base64," + base64.b64encode(_png()).decode("ascii")]

    def fake_clean(photo, model_path, notify=None, **options):
        cleans.append(options)
        return Image.new("RGB", (1200, 1500), (250, 247, 240)), []

    face = tmp_path / "aurora.png"
    face.write_bytes(_png((180, 140, 120), (400, 500)))
    monkeypatch.setattr(main, "generate_text_with_openrouter", fake_text)
    monkeypatch.setattr(main, "generate_image_with_openrouter", fake_image)
    monkeypatch.setattr(photo_cleanup, "clean_photo", fake_clean)
    monkeypatch.setattr(casting, "testimonial_photos", lambda: [face])
    photo = tmp_path / "pezzo.jpg"
    Image.new("RGB", (900, 1200), (40, 110, 60)).save(photo, "JPEG")

    main.run_agency(str(photo), "", subtype="collana")

    plan = next(p for p in prompts if "art director del sito" in p)
    assert "Ricetta: bijoux" in plan and "(collana)" in plan
    assert cleans[0].get("fill") == categorie.subtype_fill("collana")  # None finché la scala per tipo non è tarata
    worn_prompt, worn_refs = next((p, r) for p, r in images if "anklet" in p)
    # Aurora's photo goes first, the piece second, and the prompt says which is which
    assert isinstance(worn_refs, list) and worn_refs[0] == face and worn_refs[1] == photo
    assert "Image 1: the woman" in worn_prompt and "Image 2: the product" in worn_prompt


# -- T4: storyboard e scene video ------------------------------------------------------------------------------
STORYBOARD = {"title": "t", "shots": [{"purpose": "hook", "source": "ai", "duration": 4}]}


@pytest.mark.parametrize(
    ("analysis", "video_model", "expected_type"),
    [
        ("- Categoria esatta: Anello in argento con ametista", "seedance-2.5", "(anello)"),
        ("- Categoria esatta: Borsa a spalla in cuoio", "kling-3-std", "(borsa)"),
        ("- Categoria esatta: Gonna lunga ricamata", "kling-4", "(capo sotto)"),
        ("- Categoria esatta: Sciarpa di lana", "seedance-2.5", "(sciarpa)"),
    ],
)
def test_the_storyboard_reads_the_video_knowledge(analysis, video_model, expected_type, monkeypatch, tmp_path):
    seen = []
    monkeypatch.setattr(reel_studio, "generate_text_with_openrouter", lambda *a, **k: seen.append(a[2]) or json.dumps(STORYBOARD))
    state = {
        "id": "r1", "format": "reel", "target_seconds": 12, "clips": [], "photos": ["a.jpg"], "analysis": analysis,
        "brief": "", "recipe": "", "api_key": "k", "text_model": "m", "video_model": video_model,
        "keyframe_model": "openai-direct/gpt-image-2.5-flare",
    }
    reel_studio.agent_storyboard(state, tmp_path / "a.jpg")
    prompt = seen[0]
    video_name = "Seedance 2.5" if "seedance" in video_model else "Kling"
    assert f"MODELLO VIDEO ({video_name})" in prompt and "Struttura del prompt per i video" in prompt
    assert "Durata e movimento sicuri" in prompt and "Valutazione dei video" in prompt
    assert "Struttura del prompt per le foto" in prompt and "Conoscenza: GPT Image" in prompt
    assert expected_type in prompt
    assert "Gioielli piccoli: preferisci movimenti lenti" not in prompt  # la regola a mano duplicava regia-reel.md
    assert len(prompt.split()) < MAX_PROMPT_WORDS


@pytest.mark.parametrize("model", prompt_lab.VIDEO_MODELS)
def test_the_fucina_scenes_follow_the_chosen_video_model(model):
    lab = {"category": "abbigliamento", "subtype": "capo", "garment_cut": "sopra", "analisi": "gilet", "scenes_model": model}
    prompt = prompt_lab.scenes_prompt(lab, "", "")
    header = {"Seedance 2.5": "Conoscenza: Seedance", "Kling": "Conoscenza: Kling", "Genjutsu": "Conoscenza: Genjutsu"}[model]
    assert header in prompt and "(capo sopra)" in prompt
    assert ("VIDEO VERO" in prompt) == (model == "Genjutsu")


# -- T6: testi -------------------------------------------------------------------------------------------------
def test_the_reel_texts_follow_the_instagram_and_human_voice_rules(monkeypatch):
    seen = []
    monkeypatch.setattr(reel_studio, "generate_text_with_openrouter", lambda *a, **k: seen.append(a[2]) or "{}")
    reel_studio.agent_copy({"format": "reel", "storyboard": {"shots": []}, "analysis": "", "text_model": "m", "recipe": ""}, "k")
    assert "# Instagram (caption e Storie)" in seen[0] and "Come suona un testo scritto da una persona" in seen[0]


def test_the_cover_and_the_site_texts_carry_the_shop_rules():
    import casting
    import reel_kit

    cover = reel_kit.poster_prompt("Non sono semplici orecchini.")
    assert casting.never_line() in cover and "serif" in cover
    assert "# Instagram" in main.platform_rules() and "Google" in main.platform_rules()


# -- T5: post con testo ----------------------------------------------------------------------------------------
def test_text_check_is_letter_by_letter_with_accents():
    assert post_grafica.text_matches("Scrivici, ti diciamo se è disponibile.", "scrivici, ti diciamo se è disponibile")
    assert not post_grafica.text_matches("è disponibile", "e disponibile")
    check = post_grafica.check_text({"titolo": "Non sono semplici orecchini.", "altro": ["29€"]}, "Non sono semplici orecchini.")
    assert not check["ok"] and "inventati" in check["problems"][0]
    with pytest.raises(ValueError):
        post_grafica.clean_text("Te lo mettiamo da parte!")
    assert post_grafica.format_price("") == "" and post_grafica.format_price("29") == "29 €"


@pytest.mark.parametrize("model", list(post_grafica.POST_MODELS))
def test_the_post_prompt_has_title_model_knowledge_and_no_logo(model):
    prompt = post_grafica.post_prompt("look", "Non sono semplici orecchini.", "", "orecchini", "", model, 1)
    assert '"Non sono semplici orecchini."' in prompt and "(orecchini)" in prompt
    assert f"Conoscenza: {model}" in prompt and "no logo" in prompt and "Image 2: the real product" in prompt


@pytest.fixture()
def mission(tmp_path, monkeypatch):
    output_dir = server.OUTPUT_DIR / "20261120_test_post"
    (output_dir / "07_SHOWCASE").mkdir(parents=True, exist_ok=True)
    (output_dir / "07_SHOWCASE" / main.REAL_PHOTO_NAME).write_bytes(_png())
    payload = {
        "run_id": "20261120_100000_abc123",
        "brief": "orecchini a fiore 29€",
        "results": {"output_dir": output_dir.name, "subtype": "orecchini"},
    }
    monkeypatch.setattr(server, "_find_mission_payload", lambda run_id: payload if run_id == payload["run_id"] else None)
    return payload, output_dir


def test_outfit_with_prices_draws_the_tags_on_the_real_photo(mission):
    payload, output_dir = mission
    items = [{"name": "Orecchini a fiore", "price": "29", "reference": "M-ABCD", "shop": "17"}, {"name": "Borsa", "price": ""}]
    response = client.post(
        f"/missions/{payload['run_id']}/post/etichette",
        files={"foto": ("flat.png", _png((90, 120, 160)), "image/png")},
        data={"items": json.dumps(items)},
    )
    assert response.status_code == 200, response.text
    entry = response.json()
    assert entry["aiGenerated"] is False and entry["files"][0]["aiGenerated"] is False
    with Image.open(server.OUTPUT_DIR / entry["files"][0]["src"]) as image:
        assert image.size == post_grafica.POST_SIZE
    assert entry["items"][1]["price"] == ""  # nessun prezzo inventato
    listed = client.get(f"/missions/{payload['run_id']}/post").json()
    assert listed["items"][0]["id"] == entry["id"] and listed["price"] == "29 €"


def test_a_wrong_title_is_retried_then_written_by_the_code(mission, monkeypatch):
    import reel_kit

    payload, output_dir = mission
    prompts = []

    def fake_generate(api_key, model, prompt, images, destination, aspect_ratio="9:16"):
        prompts.append((model, prompt))
        destination.write_bytes(_png())
        return destination

    monkeypatch.setattr(reel_kit, "generate_image_multi", fake_generate)
    monkeypatch.setattr(post_grafica, "read_text", lambda *a: {"titolo": "Non sono semplici orechini", "sottotitolo": "", "altro": []})
    response = client.post(f"/missions/{payload['run_id']}/post/titolo", json={"title": "Non sono semplici orecchini.", "model": "Nano Banana"})
    assert response.status_code == 200, response.text
    entry = response.json()
    assert entry["aiGenerated"] is True and entry["model"] == "Nano Banana" and entry["text_written_by"] == "codice"
    assert len(prompts) == 3 and all(m == post_grafica.POST_MODELS["Nano Banana"] for m, _ in prompts)
    assert "No text of any kind" in prompts[-1][1]


def test_a_right_title_is_kept(mission, monkeypatch):
    import reel_kit

    payload, _ = mission
    monkeypatch.setattr(reel_kit, "generate_image_multi", lambda *a, **k: a[4].write_bytes(_png()) or a[4])
    monkeypatch.setattr(post_grafica, "read_text", lambda *a: {"titolo": "Non sono semplici orecchini.", "sottotitolo": "", "altro": []})
    entry = client.post(f"/missions/{payload['run_id']}/post/titolo", json={"title": "Non sono semplici orecchini."}).json()
    assert entry["text_written_by"] == "ai" and entry["model"] == "GPT Image"


def test_the_carousel_has_three_slides_and_one_caption(mission, monkeypatch):
    import reel_kit

    payload, _ = mission
    plan = {
        "slides": [{"titolo": f"Look {i}", "prompt_en": f"look {i}"} for i in range(1, 4)],
        "scena_en": "warm stone courtyard",
        "caption": "Tre modi per portarli. Scrivici, ti diciamo se è disponibile",
    }
    monkeypatch.setattr(main, "generate_text_with_openrouter", lambda *a, **k: json.dumps(plan))
    slide_prompts = []
    monkeypatch.setattr(reel_kit, "generate_image_multi", lambda *a, **k: slide_prompts.append(a[2]) or a[4].write_bytes(_png()) or a[4])
    response = client.post(f"/missions/{payload['run_id']}/post/carosello", json={"theme": "tre-modi"})
    assert response.status_code == 200, response.text
    entry = response.json()
    assert len(entry["files"]) == 3 and entry["aiGenerated"] is True
    assert "Rif." in entry["caption"] or "M-" in entry["caption"]
    assert all("warm stone courtyard" in p for p in slide_prompts)

def test_the_woman_gets_a_fresh_outfit_for_the_place_not_the_one_in_the_reference_photos():
    import casting
    import main
    import post_grafica

    site = main.controlled_site_prompt("worn on the hand", "worn", woman="Aurora", woman_photos=2)
    post = post_grafica._refs_line(2)
    for text in (site, post):
        assert casting.OUTFIT_RULE in text and "warm, elegant" in text
    assert casting.OUTFIT_RULE not in main.controlled_site_prompt("clean", "clean")
    assert casting.OUTFIT_RULE not in post_grafica._refs_line(0)


def test_ring_bracelet_and_anklet_show_only_the_body_part_with_no_face_and_no_woman():
    import categorie
    import main

    for subtype in ("anello", "bracciale", "cavigliera"):
        text = main.controlled_site_prompt(
            "worn on the hand", "worn", woman="Aurora, green eyes", woman_token="@MODELLA", woman_photos=2, subtype=subtype
        )
        assert "NO FACE" in text and "Aurora" not in text and "@MODELLA" not in text and "Images 1-2" not in text, subtype
    earrings = main.controlled_site_prompt("worn", "worn", woman="Aurora, green eyes", woman_photos=2, subtype="orecchini")
    assert "Aurora" in earrings and "NO FACE" not in earrings
    assert not categorie.is_faceless("collana") and not categorie.is_faceless("")


def test_the_studio_remembers_a_prompt_job_that_is_running_and_how_it_ended():
    from api import server

    draft = "bozza-prova"
    assert server._lab_begin(draft, "analisi") is True
    assert server._lab_begin(draft, "scene") is False  # no second job at the same time for the same piece
    assert server._lab_public(draft, None)["running"] == "analisi"
    try:
        server._lab_guarded(draft, lambda: (_ for _ in ()).throw(ValueError("chiave non valida")))
    except ValueError:
        pass
    state = server._lab_public(draft, None)
    assert state["running"] == "" and "chiave non valida" in state["failed"]
    assert server._lab_begin(draft, "analisi") is True and server._lab_public(draft, None)["failed"] == ""
    server._lab_guarded(draft, lambda: None)
