# Ricerca: contenuti AI per I Monili — immagini OpenAI, video Higgsfield, Instagram

Ricerca del 24 ottobre 2026. Le fonti ufficiali sono segnate come tali; il resto è pratica di settore
(blog, guide di terze parti) e va trattato come ipotesi da testare sui nostri numeri.

---

## 1. Sintesi in 8 punti

1. **Il modello immagini OpenAI più recente è GPT-Image-2.5** (8 settembre 2026), in due varianti API:
   **Flare** (default, qualità superiore a GPT-Image-2 con latenza dimezzata) e **Sunburst** (più lento, più
   controllo negli edit). L'app oggi usa `openai/gpt-5.4-image-2` via OpenRouter, cioè la generazione precedente:
   **GPT-Image-2.5 su OpenRouter non c'è ancora**, serve una chiave OpenAI diretta.
2. **Per non deformare il gioiello**: dare le immagini con un ruolo numerato ("Image 1: foto prodotto…"),
   scrivere "cambia solo X, tieni tutto il resto identico" e **ripetere la lista di cosa preservare a ogni tentativo**.
3. **Testo nelle immagini** (copertine poster): testo tra virgolette, "esattamente, una sola volta", tipografia
   descritta come vincolo, qualità alta.
4. **Video Kling 3.0**: il fotogramma iniziale è l'ancora; il prompt descrive **cosa cambia** rispetto a quel
   fotogramma, **un solo movimento di camera per inquadratura**. Accetta anche un **fotogramma finale**: possiamo
   chiudere ogni scena sulla foto vera del prodotto.
5. **Video Seedance 2.5**: un unico blocco di testo con sezioni fisse (stile, scena, soggetti, primo fotogramma,
   inquadrature con tempi, ottica, camera, luce, audio), conteggi bloccati ("esattamente due orecchini"),
   vincoli positivi oltre ai negativi, ogni taglio su un movimento.
6. **Instagram premia tempo di visione, like per copertura e soprattutto invii in DM per copertura**
   (Mosseri, gennaio 2025). Per il 2026 Instagram ha dichiarato come priorità l'**originalità**.
7. **Regola nuova dal 31 agosto 2026**: i profili che hanno come protagonista una **persona generata dall'AI**
   senza l'etichetta "AI-generated profile" vengono **penalizzati in copertura**. Per un negozio che usa ogni tanto
   una modella AI la regola non è chiara: vedi §5.
8. **Per un negozio locale l'AI deve fare da supporto, non sostituire il reale**: mani vere, negozio vero,
   gioiello vero come fotogramma finale, modella AI dichiarata.

---

## 2. Immagini con OpenAI (GPT-Image-2 / 2.5)

### Modelli
| Modello | Uscita | Note |
|---|---|---|
| GPT-Image-2 (`gpt-image-2`) | aprile 2026 | introduce il ragionamento nella generazione; molto bravo con il testo. È quello che usiamo via OpenRouter |
| **GPT-Image-2.5 Flare** (`gpt-image-2.5-flare`) | 8 settembre 2026 | default consigliato da OpenAI: più qualità di GPT-Image-2, metà latenza |
| **GPT-Image-2.5 Sunburst** (`gpt-image-2.5-sunburst`) | 8 settembre 2026 | per lavori "premium" con edit più controllati; più lento |

Prezzo riportato da fonti secondarie: ~30 $ per milione di token in uscita per entrambi (da verificare sulla
pagina prezzi OpenAI). Un `gpt-image-2.5` senza suffisso risulta "model not found".

### Tecniche (guida ufficiale OpenAI)
- **Ordine fisso del prompt**: scena/sfondo → soggetto → dettagli chiave → vincoli. Indicare l'**uso finale**
  ("copertina Reel Instagram", "pubblicità") perché fissa il livello di rifinitura.
- **Modello leggibile, non formule astute**: segmenti brevi etichettati, sempre lo stesso schema.
- **Fotorealismo**: scrivere "photorealistic"; materiali, texture e luce con nomi precisi. I dati tecnici della
  fotocamera vengono interpretati in modo approssimativo: usarli per l'atmosfera generale.
- **Persone**: dire inquadratura, sguardo, interazione con l'oggetto ("mano sinistra sfiora l'orecchino").
- **Edit con riferimenti, per preservare il prodotto**:
  - "Change only X. Keep everything else exactly the same."
  - **ripetere a ogni iterazione** la lista da preservare (forma, pietre, colori, metallo, proporzioni);
  - per gli edit chirurgici bloccare anche saturazione, contrasto, angolo di camera, oggetti attorno.
- **Più immagini insieme**: nominarle per indice e ruolo, e dire come interagiscono:
  "Image 1: product photo (the earrings, must stay identical). Image 2: brand model reference (same face and hair).
  Put the earrings from Image 1 on the woman from Image 2; match lighting, scale and shadows."
- **Persona coerente**: "Do not redesign the character", ripetendo ogni volta i tratti fisici.
- **Testo nell'immagine**: testo tra virgolette, "EXACT, verbatim, no extra characters", "render the headline
  exactly once"; per nomi particolari scriverli lettera per lettera; descrivere font, dimensione, colore, posizione.
- **Qualità**: `high` per testo piccolo, primi piani e edit su identità/prodotto; `low/medium` per bozze.
- **Iterare un cambiamento alla volta** ("luce più calda", "togli l'oggetto in più"), non riscrivere tutto.

### Schema prompt fotogramma gioiello (da usare nell'app)
```
USE: vertical 9:16 first frame for an Instagram Reel of a jewelry boutique.
IMAGE 1: product photo — the exact piece. IMAGE 2 (optional): brand model reference.
SCENE: <luogo, superficie, sfondo crema/neutro caldo>
SUBJECT: <chi/cosa, posa, interazione con il gioiello>
LIGHT: <es. warm window light from the left, small hard highlight to make the stones sparkle>
COMPOSITION: <inquadratura, posizione del gioiello nel terzo superiore, spazio libero per il testo>
PRESERVE (repeat every time): same shape, same stones and their exact cut and count, same colors,
same metal finish, same proportions. Do not redesign, simplify or add details.
STYLE: photorealistic, natural, not over-retouched. No text, no logos, no watermark.
```

---

## 3. Video professionali con Higgsfield

### Kling 3.0 (image-to-video) — fonti: Higgsfield, fal, Morphic, Masonry
- **Il fotogramma è l'ancora**: il prompt descrive **cosa si muove e come cambia** a partire da quell'immagine,
  non la scena da capo.
- **Un solo movimento di camera per inquadratura.** Se il movimento "scappa", semplificare il prompt e lasciare
  che i fotogrammi (iniziale/finale) guidino.
- **Ordine del prompt** (Masonry): soggetto + azione → camera → ambiente e luce → movimento e tempi →
  **cosa non deve cambiare**.
- **Fotogramma finale** (`last_image_url`): far finire la scena sulla **foto vera del prodotto** è il modo più
  sicuro per mostrare il gioiello esatto.
- **Multi-shot**: fino a 6 inquadrature in una sola generazione (3-15 s totali), ognuna con il suo prompt e la
  sua durata. Le transizioni interne restano coerenti di luce e soggetto.
- Kling conserva bene testi e dettagli dell'immagine di partenza: utile per la pubblicità.

### Seedance 2.5 — fonte: guida ufficiale Higgsfield
- **Un unico blocco con sezioni in ordine fisso**: GLOBAL STYLE, SCENE, CHARACTERS, LOCATION,
  FIRST FRAME AND BLOCKING, inquadrature con tempi, OPTICS, CAMERA, PHYSICS, LIGHTING, AUDIO.
  Una sezione saltata produce un difetto prevedibile: luogo vago → deriva tra i tagli; blocking mancante →
  inizio instabile.
- **Timeline con tempi**: "0.0s to 3.0s, SEGMENT 1, close-up, slow dolly-in. HARD CUT." Dichiarare all'inizio
  durata totale, numero di segmenti e tempi dei tagli.
- **Riferimenti con un ruolo preciso**: "identity and wardrobe locked to the reference", "ignore the reference
  backdrop", per il prodotto "inherited exactly from the reference".
- **Prodotto descritto in modo esaustivo** (materiale, colore, dettagli) e per stati: "every detail per the asset
  when resting, when touched, when worn".
- **Conteggi bloccati**: "exactly two earrings, never three".
- **Vincoli positivi oltre ai negativi** ("NOT golden hour" + cosa rendere al suo posto).
- **Ogni taglio cade su un movimento**, mai su una posa ferma; niente rallenty non motivati.
- Audio di default: "No music, no discernible dialogue" (la musica la mettiamo da Instagram).

### Movimenti di camera che funzionano per i gioielli
- **slow push-in** verso la pietra centrale (hook dei primi secondi);
- **orbit lento** sul profilo di un anello o di un orecchino;
- **pull-back reveal**: dal dettaglio al look completo;
- **rack focus**: dalla pietra al viso della modella;
- **mano che entra in campo** e solleva il gioiello (gesto umano = credibilità).
Luce: una sorgente calda laterale più un piccolo punto di luce dura per far brillare le pietre.
Evitare rotazioni veloci e whip-pan sui pezzi piccoli: è lì che le pietre si "sciolgono".

### Schema prompt video (Kling) da usare nell'app
```
SUBJECT & ACTION: <cosa succede a partire dal fotogramma>
CAMERA: <un solo movimento, es. slow push-in toward the center stone over 4 seconds>
LIGHT: <warm side light, a small hard highlight sweeps across the stones>
TIMING: <es. motion starts immediately, settles in the last second>
PRESERVE: the jewelry keeps its exact shape, stones, count and metal in every frame;
no morphing, no extra elements, no text.
```

---

## 4. Instagram nel 2026: cosa conta davvero

- **Segnali principali dei Reel** (Mosseri, gennaio 2025): **tempo di visione**, **like per copertura**,
  **invii in DM per copertura**. Gli invii sono quelli che portano i Reel a chi non ti segue.
- **Originalità**: priorità dichiarata per il 2026. Contenuti ripostati, o con il watermark di altre piattaforme,
  vengono penalizzati. Il contenuto AI fatto da noi e pubblicato direttamente conta come originale.
- **Primi 3 secondi**: è lì che si decide se il video continua a girare. Mettere testo a schermo subito (molti
  guardano senza audio), aprire con il risultato e non con la preparazione, cambiare qualcosa ogni 3-5 secondi.
- **Chiusura che spinge l'invio**: oltre a "scrivici in DM", provare **"Mandalo a chi te lo regalerebbe"**:
  genera invii, cioè il segnale più forte per la copertura.
- Orari: le prove di settore dicono che la frequenza conta più dell'orario esatto (dato aneddotico).

## 5. Contenuti AI: etichette e rischio copertura

- **Etichetta per post "Info sull'AI"**: obbligatoria per video e immagini fotorealistici generati o alterati con
  l'AI. Non risulta da fonti ufficiali una penalizzazione di copertura legata a questa etichetta.
- **Etichetta di profilo "AI-generated profile"** (dal 31 agosto 2026): riguarda i profili che hanno **come
  protagonista una persona generata dall'AI**. Senza etichetta → copertura ridotta nel feed e nei consigliati
  (non un ban). Per un negozio con persone vere che usa ogni tanto una modella AI la regola **non è chiara**
  nelle fonti trovate.
- **Cosa facciamo per stare tranquilli**:
  1. etichetta "Info sull'AI" su ogni post con la modella AI;
  2. la Modella Monili **non diventa un personaggio** con nome, storia e "vita" propria: è una modella da catalogo,
     non un'influencer finta;
  3. il profilo resta centrato su cose vere: negozio, mani, gioielli veri, Ravenna.

---

## 6. Cosa cambiare nell'app (proposte)

| # | Modifica | Perché | Costo |
|---|---|---|---|
| 1 | Motore immagini **OpenAI diretto con GPT-Image-2.5 Flare** (Sunburst per le copertine poster) | modello più nuovo, più qualità, metà latenza | serve `OPENAI_API_KEY`; prezzo simile all'attuale |
| 2 | Prompt fotogrammi con **immagini indicizzate per ruolo** e **lista da preservare ripetuta** | meno gioielli deformati | nessuno |
| 3 | **Fotogramma finale = foto vera del prodotto** (Kling `last_image_url`) per le scene dettaglio | il gioiello esatto appare sempre a fine scena | nessuno |
| 4 | Prompt video con lo schema soggetto → camera → luce → tempi → preserva, un movimento per scena | movimenti più puliti | nessuno |
| 5 | **Hook testuale nel primo secondo** e chiusura "Mandalo a chi…" nelle ricette | tempo di visione + invii | nessuno |
| 6 | Opzione Kling **multi-shot** (una generazione per tutto il Reel) | coerenza di luce e soggetto tra le scene | stesso prezzo al secondo |

---

## Fonti
- OpenAI — [GPT Image Generation Models Prompting Guide](https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide) (ufficiale)
- OpenAI — [Introducing ChatGPT Images 2.5](https://openai.com/index/introducing-chatgpt-images-2-5/), [OpenAI Developers su X](https://x.com/OpenAIDevs/status/2097399255975813387), [Community OpenAI](https://community.openai.com/t/introducing-gpt-images-2-5-in-the-api-and-chatgpt/1395897) (ufficiali)
- [Wikipedia — GPT Image](https://en.wikipedia.org/wiki/GPT_Image); [tosea.ai — nomi API 2.5](https://tosea.ai/blog/gpt-image-2-5-complete-guide); [aicatchup — prezzi](https://aicatchup.com/news/openai-chatgpt-images-2-5-gpt-image-2-5)
- Higgsfield — [Kling 3.0 user guide](https://higgsfield.ai/blog/Kling-3.0-is-on-Higgsfield-User-Guide-AI-Video-Generation), [Seedance 2.5 prompting guide](https://higgsfield.ai/blog/seedance-2-5-prompting-guide), [API docs](https://docs.higgsfield.ai/docs/models/kling-3/standard-image-to-video) (ufficiali)
- [fal — Kling 3.0 prompting guide](https://blog.fal.ai/kling-3-0-prompting-guide/), [Morphic — Kling 3.0](https://morphic.com/resources/how-to/kling-3.0-guide), [Masonry — Kling product ads](https://masonry.so/blog/introducing-kling-3-best-prompts-and-examples), [Kapwing — Seedance 2.5](https://www.kapwing.com/resources/how-to-prompt-seedance-2-5-a-guide-for-ai-video-creators/)
- Instagram — [SocialPilot](https://www.socialpilot.co/blog/instagram-reels-algorithm), [Exemplary — originalità](https://exemplary.ai/blog/instagram-algorithm-original-content), [ReelDrop — segnali](https://www.reeldrop.io/learn/instagram-algorithm), [Metricool — guida Reels](https://metricool.com/instagram-reels-guide/)
- Etichette AI — [Kompozy — AI profile rules](https://kompozy.io/guides/instagram-ai-profile-disclosure-rules), [TechSpot](https://techspot.com/news/113695-instagram-cracks-down-ai-accounts-pretending-human), [Kompozy — AI labels](https://kompozy.io/guides/instagram-ai-content-detection-and-labeling)
- Gioielli — [Luma — AI product video jewelry](https://lumalabs.ai/news/ai-product-video-generators-jewelry-brands), [TrueFan — jewelry showcase](https://www.truefan.ai/blogs/ai-product-showcase-jewelry)
