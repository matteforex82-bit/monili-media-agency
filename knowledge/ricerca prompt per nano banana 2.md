Ti lascio una mini‑guida pratica, pensata proprio per Nano Banana 2 / Gemini su product photography e image‑to‑image, che puoi trasformare in knowledge base per la tua app.  

***

## 1. Best practice ufficiali per image‑to‑image con Gemini / Nano Banana 2

- **Passa sempre “immagine + testo”**: nei client ufficiali (API, AI Studio, Vertex) per edit devi inviare il file immagine come `part` e un’istruzione testuale tipo: “Edit this image to…”. [github](https://github.com/google-gemini/gemini-image-editing-nextjs-quickstart)
- **Chiedi cosa vuoi aggiungere/cambiare, non solo cosa evitare**: la guida “Gemini image generation best practices” insiste su richieste specifiche, contestualizzate, step‑by‑step (“replace the white background with a natural wooden surface…”) invece di prompt vaghi o solo negativi. [docs.cloud.google](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/gemini-image-generation-best-practices)
- **Usa multi‑turn editing per rifinire**: Gemini 2.x/3.x supporta conversazioni iterative, così puoi dire “rendi la luce più calda”, “avvicina l’inquadratura sulle pietre” senza riscrivere tutto. [developers.googleblog](https://developers.googleblog.com/experiment-with-gemini-20-flash-native-image-generation/)
- **Mantieni il contesto con thought signatures (se usi API avanzate)**: per le versioni 3 Pro / 3.1 Flash Image Google consiglia di riusare i “thought signatures” per mantenere coerenza di stile e dettagli tra più turni di editing. [docs.cloud.google](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/thought-signatures)
- **Visual anchor / reference image**: guide reali su prodotto (Gemini 2.5 Flash e Nano Banana Pro per Amazon) lavorano partendo da un’unica “master image” del prodotto e la riusano come riferimento in tutte le varianti per mantenere forma, colore e texture coerenti. [bananai](https://bananai.net/blog/tutorials/nano-banana-pro-prompts-amazon-listing-images)
- **Blocca i 4 elementi chiave per serie e‑commerce**: luce, angolo di camera, stile sfondo e temperatura colore vanno mantenuti uguali in tutti gli scatti di un set (white background, lifestyle, macro, comparativa) per dare coerenza visiva. [help.apiyi](https://help.apiyi.com/en/ecommerce-product-photo-prompt-templates-nano-banana-en.html)

***

## 2. Template base per product photography fotorealistica

I template e‑commerce pro per Nano Banana 2 fissano struttura e parametri fissi (main image, scene, detail, comparison…), che tu puoi adattare a gioielli e accessori. [help.apiyi](https://help.apiyi.com/en/ecommerce-product-photo-prompt-templates-nano-banana-en.html)

**Template generico “hero product shot” (image‑to‑image)**  
(Usalo caricando la tua foto reale come riferimento)

> Ruolo (opzionale, se il tool lo supporta):  
> “Sei un fotografo pubblicitario professionista specializzato in fotografie di prodotto per boutique di gioielli e moda.”  
>  
> Istruzione:  
> “Usando esclusivamente questo prodotto come riferimento visivo, genera una fotografia commerciale ad altissima qualità.  
>  
> **Reference fidelity**: mantieni il prodotto identico all’originale in forma, dimensioni, proporzioni, colore, materiali, pietre e texture, senza cambiare nulla della progettazione o del design.  
>  
> **Scene**: [descrivi lo sfondo: es. ‘set da boutique di lusso con piano in marmo chiaro e sfondo sfocato color crema’].  
>  
> **Lighting**: luce da studio morbida, direzione [es. ‘45 gradi da sinistra’], con riflessi controllati che evidenziano i materiali e riducono i riflessi bruciati sulle superfici lucide.  
>  
> **Camera / lens**: fotografia realistica, lente equivalente 50mm, profondità di campo ridotta, messa a fuoco nitidissima sul prodotto, sfondo leggermente sfocato.  
>  
> **Styling & props**: aggiungi solo pochi props coerenti con una boutique reale [es. ‘piccolo supporto trasparente, qualche riflesso morbido, nessun testo o logo’].  
>  
> **Constraints**: non modificare o deformare il prodotto, non aggiungere loghi, testo, watermark, interfacce chat o telefoni, evita qualsiasi elemento che sembri finto o cartoonesco. Mantieni uno stile totalmente fotorealistico.”

***

## 3. Template per jewelry try‑on (anelli, orecchini, collane)

Nei casi reali di Nano Banana Pro per e‑commerce si usa la reference image del prodotto e si compone una nuova scena con modella o mano come “contesto”. [jumpfly](https://www.jumpfly.com/blog/how-to-write-high-performance-image-prompts-for-nanobanana-using-gemini/)

### Anelli su mano

> “Usando questo anello come riferimento visivo, genera una foto fotorealistica di una mano umana reale che indossa esattamente questo anello.  
>  
> **Reference fidelity**: mantieni il design dell’anello identico all’originale in forma, spessore, proporzioni, colore del metallo e delle pietre, incisioni e texture. Nessuna deformazione o semplificazione.  
>  
> **Scene**: mano femminile naturale appoggiata su un piano neutro elegante [es. ‘tavolo in marmo chiaro in boutique’], inquadratura ravvicinata dalle nocche fino a metà dita.  
>  
> **Lighting**: luce morbida da studio, leggermente laterale, che fa brillare le pietre senza bruciare i dettagli; ombre morbide e realistiche.  
>  
> **Hand details**: anatomia delle dita corretta, proporzioni realistiche, pelle naturale con texture sottile, unghie curate con smalto neutro, nessun difetto eccessivo ma aspetto umano credibile, non plastico.  
>  
> **Constraints**: non cambiare il design dell’anello, non aggiungere altri anelli, non mostrare loghi, testo o watermark, niente pose bizzarre o irreali.”

### Orecchini indossati

> “Usando questi orecchini come riferimento visivo, crea un ritratto fotorealistico di una modella che li indossa.  
>  
> **Reference fidelity**: mantieni dimensioni, lunghezza, forma, colore del metallo e delle pietre identici all’immagine originale.  
>  
> **Scene**: mezzobusto della modella in ambiente di boutique elegante, sfondo sfocato, focus sull’orecchio e sul profilo del viso.  
>  
> **Lighting**: luce morbida laterale che disegna il profilo del viso e fa brillare gli orecchini, utanare riflessi metallici troppo duri.  
>  
> **Model**: pelle naturale, texture realistica, trucco leggero da boutique, acconciatura che lascia l’orecchio scoperto.  
>  
> **Constraints**: nessun gioiello extra vicino alle orecchie, niente loghi sullo sfondo, niente testo, nessun effetto cartone animato.”

### Collane al collo

> “Usando questa collana come riferimento, genera una foto fotorealistica di una modella che indossa la collana al collo.  
>  
> **Reference fidelity**: mantieni esattamente lunghezza, forma della catena, colore del metallo e dei ciondoli, disposizione delle pietre.  
>  
> **Scene**: inquadratura dal busto al collo, abbigliamento neutro che valorizza la collana, sfondo sfocato da boutique.  
>  
> **Lighting**: luce frontale morbida + leggero controluce per creare riflessi sulle pietre.  
>  
> **Constraints**: nessuna deformazione della collana, nessun testo, nessun logo visibile, stile fotografico realistico.”

***

## 4. Template per abbigliamento indossato da modella AI

La ricerca su fashion + generative AI e le pipeline professionali per e‑commerce insistono sulla fedeltà a tessuto, taglio e struttura del capo. [ojs.aaai](https://ojs.aaai.org/index.php/AAAI-SS/article/view/36056)

> “Usando questo capo di abbigliamento come riferimento (shape, pattern e tessuto), crea una foto fotorealistica di una modella che lo indossa.  
>  
> **Reference fidelity**: mantieni identici colore, pattern, tessuto (es. cotone, seta, lana), lunghezza, taglio e proporzioni del capo. Non modificare il design, non cambiare scollatura, lunghezza maniche o vestibilità.  
>  
> **Scene**: foto editoriale semplice per boutique, modella in piedi in un ambiente minimal e luminoso [es. ‘boutique contemporanea con pareti chiare’].  
>  
> **Lighting**: luce morbida uniforme che mostra chiaramente pieghe del tessuto e drappeggio, senza ombre dure.  
>  
> **Camera / framing**: inquadratura a figura intera verticale (9:16) o mezzobusto (4:5) a seconda del formato, leggera prospettiva frontale.  
>  
> **Styling**: abbina il capo a accessori minimali che non rubano la scena, mantenendo il focus sul prodotto principale.  
>  
> **Constraints**: non alterare la struttura del capo, non cambiare colore o pattern, niente loghi inventati, niente testo o watermark nell’immagine.”

***

## 5. Frasi di controllo e “negative prompt” utili

La documentazione Google suggerisce di focalizzarsi su ciò che vuoi vedere, ma nella pratica commerciale alcuni vincoli espliciti aiutano, se formulati come requisiti chiari, non solo come “no…”. [docs.cloud.google](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/gemini-image-generation-best-practices)

**Formulazioni positive (consigliate):**

- “mani realistiche con anatomia corretta e proporzioni naturali”  
- “pelle dall’aspetto naturale, con texture sottile, non plastica, non cerata”  
- “gioiello non deformato, con bordi netti e dettagli nitidi”  
- “nessun testo leggibile nell’immagine, nessun logo o marchio visibile”  
- “nessun watermark, nessuna UI di chat, nessun telefono sullo schermo”  

**Se vuoi comunque usare frasi di esclusione (da mettere a fine prompt, come blocco ‘constraints’):**

- “evita mani deformi, dita fuse o numero di dita errato”  
- “evita pelle plastica, troppo levigata o simile a un render 3D”  
- “evita loghi inventati, scritte di marca e simboli casuali”  
- “evita qualsiasi testo, watermark o interfaccia digitale nell’immagine”  

Ricorda però che per Gemini / Nano Banana non esiste il concetto di “negative prompt” tecnico alla Stable Diffusion: sono comunque solo istruzioni testuali; funzionano meglio se accompagnate da una descrizione positiva chiara di cosa deve apparire. [docs.cloud.google](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/gemini-image-generation-best-practices)

***

## 6. Strutturare il prompt in sezioni

Framework strutturati tipo SCHEMA per Gemini 3 Pro Image mostrano che suddividere il prompt in moduli coerenti aumenta molto la consistenza tra generazioni. [zenodo](https://zenodo.org/doi/10.5281/zenodo.18721380)

Per il tuo caso puoi usare sempre questo schema:

1. **Reference fidelity**  
   - Cosa deve rimanere identico all’immagine di partenza (forma, colore, materiali, proporzioni, pietre, dettagli).  
2. **Scene / environment**  
   - Tipo di ambientazione: studio, boutique, lifestyle, still life, close‑up macro, ecc.  
3. **Lighting**  
   - Tipo di luce (studio softbox, finestra, golden hour), direzione (45° da sinistra), durezza, temperatura colore.  
4. **Camera / lens**  
   - Tipo di scatto (macro, flat lay, mezzobusto, figura intera), focale virtuale (35mm, 50mm, 85mm), profondità di campo.  
5. **Styling & props**  
   - Modella, posa, outfit, eventuali oggetti di scena, palette colori.  
6. **Format / output**  
   - Rapporto d’aspetto richiesto (1:1, 4:5, 9:16), destinazione (Instagram post, story, Google Business…).  
7. **Constraints**  
   - Cosa non deve cambiare (prodotto), cosa non deve apparire (loghi, testo, watermark, UI finte, ecc.).  

Puoi scriverlo in forma naturale (“**Reference fidelity**: …”) oppure come lista di frasi brevi: Gemini gestisce bene prompt strutturati e “step‑by‑step”. [oneuptime](https://oneuptime.com/blog/post/2026-02-17-how-to-design-effective-prompts-for-gemini-models-in-vertex-ai-studio/view)

***

## 7. Esempi concreti per i diversi formati

### Instagram feed 1:1 – still life gioiello

> “Usando questo anello come riferimento, genera una fotografia di prodotto fotorealistica in formato quadrato 1:1 per un post Instagram.  
>  
> **Reference fidelity**: l’anello deve rimanere identico all’originale in forma, dimensioni, colore del metallo, pietre e incastonatura.  
>  
> **Scene**: still life su un piano in marmo chiaro, sfondo sfocato color crema, stile boutique di lusso minimal.  
>  
> **Lighting**: luce da studio morbida, proveniente da sinistra, che crea riflessi controllati sulle pietre senza bruciare i dettagli.  
>  
> **Camera / lens**: scatto ravvicinato, lente equivalente 70mm, profondità di campo ridotta che mette a fuoco solo l’anello.  
>  
> **Styling**: nessun altro gioiello, solo un supporto discreto trasparente, palette colori neutra.  
>  
> **Format / output**: composizione centrata, pensata per Instagram feed, 1:1.  
>  
> **Constraints**: non aggiungere testo, loghi, watermark o interfacce digitali; non modificare il design dell’anello.”

(La parte di formato/ratio la puoi specificare anche a livello di API o UI scegliendo 1:1 se l’interfaccia lo permette.) [skywork](https://skywork.ai/blog/nano-banana-prompts-product-photos/)

### Story verticale 9:16 – modella con collana

> “Usando questa collana come riferimento, crea una foto verticale 9:16 per una Instagram Story.  
>  
> **Reference fidelity**: la collana deve rimanere identica in forma, lunghezza, colore del metallo, disposizione delle pietre e ciondoli.  
>  
> **Scene**: modella a mezzobusto in boutique luminosa, sfondo sfocato, tono caldo e accogliente.  
>  
> **Lighting**: luce morbida frontale + leggera luce laterale per far brillare la collana, ombre dolci.  
>  
> **Camera / lens**: inquadratura verticale a mezzobusto, leggera angolazione di tre quarti.  
>  
> **Styling**: abbigliamento semplice e monocromatico per non distrarre dalla collana, trucco leggero.  
>  
> **Format / output**: composizione adatta a story 9:16, con spazio negativo sopra la testa per eventuale overlay di testo aggiunto dopo in design (non nell’immagine AI).  
>  
> **Constraints**: nessun testo o logo generato nell’immagine, niente altri gioielli vistosi, nessun effetto grafico finto.”

### Carousel coerente a 5 slide

I flussi “Amazon listing” con Nano Banana usano una master image e poi prompt per slot diversi (hero, lifestyle, macro, comparativa, ecc.) mantenendo sempre la stessa reference. [bananai](https://bananai.net/blog/tutorials/nano-banana-pro-prompts-amazon-listing-images)

Per un carousel Instagram a 5 slide, puoi definire:

1. **Slide 1 – Hero**  
   - Hero shot del prodotto, semplice e pulito (vedi template “hero” sopra).  
2. **Slide 2 – Lifestyle**  
   - Prodotto in uso (es. orecchini su modella in scena reale).  
3. **Slide 3 – Macro dettaglio**  
   - Dettaglio ravvicinato delle pietre / texture.  
4. **Slide 4 – Variazione styling**  
   - Stesso prodotto abbinato ad outfit diverso, stessa scena e luce.  
5. **Slide 5 – Group / mix**  
   - Più pezzi della stessa collezione insieme, stessa palette e stile.  

Esempio di prompt per una **slide macro dettagli**:

> “Usando la stessa reference image del prodotto delle immagini precedenti, genera uno scatto macro estremo del dettaglio principale dell’anello (pietra centrale e griffe).  
>  
> Mantieni identici colore, taglio e montatura della pietra, così come la texture e il colore del metallo.  
>  
> Usa la stessa illuminazione e lo stesso stile delle immagini precedenti per coerenza di serie.  
> Inquadratura strettissima sul dettaglio, sfondo completamente sfocato.”  

Per ogni slide, ri‑menziona brevemente “mantieni stile, luce, palette e grado di realismo uguali alle immagini precedenti” per aiutarlo a non cambiare look tra una generazione e l’altra. [philschmid](https://www.philschmid.de/gemini-image-generation-product)

### Google Business / foto boutique locale

Le linee guida informali per foto business privilegiano autenticità e contesto reale: ingresso negozio, interno, dettagli di espositori. [stradiji](https://www.stradiji.com/en/the-new-era-of-visual-editing-with-ai-gemini-2-0-flash-guide/)

> “Usando questo prodotto come riferimento, genera una foto fotorealistica scattata all’interno di una piccola boutique di gioielli italiana.  
>  
> **Reference fidelity**: il prodotto deve rimanere identico (forma, colore, proporzioni, materiali).  
>  
> **Scene**: esposizione su vetrinetta in vetro all’interno del negozio, con parte dell’arredo visibile (scaffali, luci calde), ma sfocato quanto basta.  
>  
> **Lighting**: luce calda da faretti di negozio, con riflessi realistici sul vetro e sui metalli, esposizione bilanciata.  
>  
> **Camera / lens**: foto leggermente grandangolare, inquadratura a livello degli occhi di un cliente.  
>  
> **Constraints**: nessun logo leggibile o brand inventato sulle pareti o sugli espositori, niente testo o watermark, stile fortemente realistico come una vera foto scattata in negozio.”

***

## 8. Errori comuni nei prompt che rovinano il realismo

Le guide su Gemini/Nano Banana e i casi di studio reali convergono su una serie di errori tipici. [oneuptime](https://oneuptime.com/blog/post/2026-02-17-how-to-design-effective-prompts-for-gemini-models-in-vertex-ai-studio/view)

- **Prompt troppo vaghi**: “foto bella del mio anello” senza descrivere scena, luce, inquadratura e obiettivo porta a risultati casuali.  
- **Mischiare troppi stili in una frase**: “ultra‑realistico, ma anche stile cartoon e acquerello” crea conflitti interni e degrada il fotorealismo.  
- **Non fissare un anchor di stile**: non partire da una master image coerente e non ripetere luce/angolo/colore porta a una serie di immagini disallineate. [philschmid](https://www.philschmid.de/gemini-image-generation-product)
- **Abusare di “no, no, no…”**: una lunga lista di “no” senza dire cosa vuoi davvero può confondere il modello; meglio definire prima cosa deve esserci, poi pochi vincoli mirati. [docs.cloud.google](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/gemini-image-generation-best-practices)
- **Chiedere testo/loghi dentro l’immagine**: portano spesso a scritte deformate e look “AI finto”; meglio lasciare testo e loghi alla grafica successiva. [developers.googleblog](https://developers.googleblog.com/generate-images-gemini-2-0-flash-preview/)
- **Ignorare il formato di destinazione**: non specificare 1:1, 4:5, 9:16 e tipo di shot (macro, mezzobusto, figura intera) aumenta il rischio di composizioni tagliate male. [skywork](https://skywork.ai/blog/nano-banana-prompts-product-photos/)
- **Non iterare**: Google suggerisce esplicitamente di lavorare per piccoli passi (“make the lighting warmer”, “crop closer on the ring”) invece di riscrivere tutto ogni volta. [developers.googleblog](https://developers.googleblog.com/experiment-with-gemini-20-flash-native-image-generation/)

***

## 9. Mini‑guida riutilizzabile per la tua knowledge base

Ti propongo uno **scheletro standard** che puoi salvare nella tua app e riempire a runtime con i dettagli del prodotto e del formato.

**Schema generico image‑to‑image per Nano Banana 2 / Gemini**

> “Usando questa immagine come riferimento visivo del prodotto, esegui un editing fotorealistico per creare una nuova fotografia commerciale.  
>  
> **Reference fidelity**  
> Mantieni il prodotto perfettamente identico all’originale in forma, dimensioni, proporzioni, colore, materiali, pietre, texture e dettagli.  
> Non cambiare nulla del design o della struttura del prodotto.  
>  
> **Scene / environment**  
> [descrivi l’ambientazione target: studio, boutique, lifestyle, interno negozio, ecc. + elementi chiave]  
>  
> **Lighting**  
> [descrivi tipo di luce, direzione, morbidezza, temperatura colore, eventuali riflessi desiderati]  
>  
> **Camera / lens**  
> [macro / close‑up / mezzobusto / figura intera], [focale equivalente 35/50/85mm], profondità di campo [ridotta/media], messa a fuoco sul prodotto.  
>  
> **Styling & props**  
> [modella / mano / collo / esposizione su supporto], [props ammessi e palette colori], stile coerente con una boutique reale.  
>  
> **Format / output**  
> Immagine pensata per [Instagram post 1:1 / Story 9:16 / carousel / Google Business], composizione [centrata / rule of thirds], margini adeguasti.  
>  
> **Constraints**  
> – Non modificare forma, colore o materiale del prodotto.  
> – Non aggiungere testo, loghi, marchi, watermark o interfacce digitali.  
> – Mantieni mani, pelle e corpo con anatomia corretta e aspetto naturale, non plastico.  
> – Evita qualsiasi effetto cartoonesco o stilizzato: lo stile deve essere completamente fotorealistico.”

Puoi creare varianti di questo schema per:  
- **“Still life gioiello”** (nessuna modella, solo props e sfondo).  
- **“Try‑on gioiello”** (mano/orecchio/collo).  
- **“Abbigliamento su modella”** (focus su shape e tessuto).  
- **“Scatto interno boutique”** (contesto negozio reale).  

Ogni variante riusa le stesse sezioni, cambiando solo Scene, Styling e Format: in questo modo puoi costruire una libreria di template coerente, collegata ai tuoi casi d’uso Instagram / Google Business / carousel, e passarla in modo programmatico ai tuoi agent nella tua app. [jumpfly](https://www.jumpfly.com/blog/how-to-write-high-performance-image-prompts-for-nanobanana-using-gemini/)

Se vuoi, nel prossimo passo possiamo prendere un tuo scatto reale (es. un anello della boutique) e costruire insieme 3‑4 prompt “pronti incolla” specifici per Nano Banana 2 che puoi subito testare....