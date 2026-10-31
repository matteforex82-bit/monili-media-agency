# Higgsfield: guida pratica ai video dei gioielli

Ricerca del 31 ottobre 2026, fatta il giorno del primo test in negozio. Completa la sezione 3 di
`ricerca_marketing_ai_2026.md` (24/10), che resta valida.

**Affidabilità delle fonti.** Reddit non è raggiungibile da questo PC (né dal recupero pagine né dal browser
integrato) e le ricerche web non restituiscono thread di utenti. Le fonti sono quindi: documentazione API
ufficiale (affidabile), blog di Higgsfield (affidabile sui numeri, promozionale sui giudizi), blog di terzi
(spesso venditori). **Nessuna fonte misura quanto reggono i dettagli piccoli dei gioielli**: lo scopriamo noi
col test.

---

## 1. Cosa c'è oggi su Higgsfield

### Via API (quello che usa lo Studio)
Letto dalla documentazione ufficiale `docs.higgsfield.ai`:

| Modello | Endpoint image-to-video | Durata | Fotogramma finale | Audio | Note |
|---|---|---|---|---|---|
| Kling 3.0 Standard | `kling-video/v3.0/std/image-to-video` | 3-15 s | `last_image_url` | `sound` on/off (**default on**) | multi-shot fino a 6 inquadrature (`multi_shots` + `multi_prompt`), `cfg_scale` 0-1 |
| Kling 3.0 Pro | `kling-video/v3.0/pro/image-to-video` | 3-15 s | `last_image_url` | come sopra | stesso schema dello Standard |
| Kling 3.0 4K / Turbo | `.../v3.0/4k/...`, `.../v3.0-turbo/...` | | | Turbo senza audio | Turbo è più veloce ma **non** più economico: non serve |
| Seedance 2.5 | `bytedance/seedance-2.5/image-to-video` | 4-30 s | `end_image_url` | `generate_audio` (**default true**) | `resolution` 480p/720p/1080p (default 720p); formato preso dall'immagine |
| Seedance 2.0, Wan 3.0, Kling O3/Omni | presenti | | | | non provati |

Il nostro `higgsfield_client.py` usa già i nomi giusti dei campi e spegne l'audio di entrambi (i default
sono "acceso"): **verificato, niente da correggere**.

### Solo sul sito higgsfield.ai (non via API)
- **Kling 4.0** (uscito il 15/10/2026): 3-30 s, fino a 10 fotogrammi chiave, fino a 15 riferimenti, 9:16,
  720p/1080p. **Non è nell'API**: per ora non possiamo usarlo dallo Studio.
- **"Unlimited"**: vale solo usando il sito. Tutto quello che passa da API, MCP o CLI **scala sempre crediti**.
- Le funzioni del video di Raffaele Gaito (sezione 5) sono strumenti del sito.

## 2. Quanto costa davvero

Prezzi dal blog Higgsfield (agosto-ottobre 2026), a circa 0,05 $ a credito (piano Plus). Il costo vero lo dà
l'endpoint `/estimate`, che lo Studio usa appena c'è la chiave.

| Clip da 5 s | 720p | 1080p |
|---|---|---|
| Kling 3.0 | 10 crediti (~0,50 $) | 12,5 crediti (~0,63 $) |
| Seedance 2.0 | 23 crediti (~1,15 $) | 45 crediti (~2,25 $) |
| Kling 4.0 (solo sito) | 13,75 crediti (~0,67 $) | 20 crediti (~0,98 $) |

- **Attenzione: la tabella sopra è in crediti del sito, non dell'API.** Listino vero della console API (screenshot
  di Matteo, 31/10/2026, prezzi "da" al secondo, cioè la configurazione più economica):

  | Modello | Listino | Prezzo attuale | Con "max-discount" |
  |---|---|---|---|
  | Kling 3.0 | 0,084 $ | 0,071 $ | **0,042 $** (−50%) |
  | Kling 4.0 (c'è anche via API) | 0,094 $ | 0,080 $ | 0,066 $ (−30%) |
  | Seedance 2.5 | 0,206 $ | 0,175 $ | 0,144 $ (−30%) |
  | Seedance 2.0 | 0,141 $ | 0,120 $ | 0,099 $ |
  | Wan 3.0 | 0,050 $ | 0,020 $ (−60% fino al 31/10) | 0,020 $, poi −50% |
  | Genjutsu / Genjutsu Light | 0,318 / 0,050 $ | 0,270 / 0,043 $ | 0,159 / 0,025 $ |

  Il "max-discount" si ottiene scegliendo **1 modello immagine e 2 modelli video**. Consiglio: Kling 3.0
  (motore principale, 5 s ≈ 0,21 $) più Kling 4.0 o Seedance 2.5 come riserva per i dettagli.

  **Attenzione ai prezzi "da"**: sono la modalità più economica del modello. Per l'Image to Video (quella che usiamo)
  la console dà: Kling 3.0 Standard 0,042-0,063 $/s (con sconto; 0,042 senza audio), **Kling 4.0 0,110 $/s in 720p
  fino a 0,1645 $/s in 1080p** (con sconto; senza sconto 0,157-0,235). Il "da 0,066 $" di Kling 4.0 è Video Edit e
  Reference to Video. Kling 4.0 Image to Video costa quindi circa 2,6 volte Kling 3.0: si usa solo se Kling 3.0 deforma.

  **Kling 4.0 Image to Video via API** (`kling-video/v4.0/image-to-video`, scheda su open.higgsfield.ai, 31/10):
  `image_url` (primo fotogramma, obbligatorio), `image_urls` (fino a 8 fotogrammi intermedi, in ordine, senza tempi),
  `end_image_url`, `duration` 3-30 (default 10), `resolution` 720p/1080p (**default 1080p**). Niente audio, formato
  (segue l'immagine), `cfg_scale` o multi-shot. **Collegato allo Studio il 31/10** come motore `kling-4` (720p, con
  fotogramma finale); i fotogrammi intermedi non sono ancora usati.

  Il prezzo di Seedance 2.5 "0,0738 $/s" letto sul blog era sbagliato o vecchio: via API Seedance
  costa **più del triplo** di Kling 3.0. Le stime di riserva sono state aggiornate al listino (Kling 3.0 0,071, Kling 4.0 0,134, Seedance 0,175 $/s);
  con la chiave lo Studio usa comunque `/estimate`.
- **Costo vero di una clip = prezzo × tentativi.** Higgsfield stesso dice 3-10 tentativi per clip buona (dato
  non dimostrato, ma va messo in conto). Le clip venute male ma completate **si pagano**; solo i lavori falliti
  per errore tecnico vengono rimborsati.
- Kling passa da 720p a 1080p con +25%; Seedance raddoppia. Quindi: **prove in 720p**, definitivo in 1080p.

## 3. Regole di produzione per i gioielli

Quelle già nello Studio (dalla ricerca del 24/10) restano valide: fotogramma di partenza dalla foto vera, un
solo movimento lento per scena, niente rotazioni veloci, blocco PRESERVE, niente testo nel video, audio spento.
Le novità di questa ricerca:

1. **Il gioiello deve occupare molto spazio nel fotogramma.** Un tester riporta che, con il soggetto che riempie
   almeno due terzi dell'inquadratura, le deformazioni a metà clip calano nettamente. Un orecchino piccolo su una
   donna inquadrata a mezzo busto è il caso peggiore: lì le pietre si "sciolgono". Per i dettagli, primi piani.
2. **Fotogramma iniziale e finale devono somigliarsi**: stessa luce, stessa ottica, stessa distanza. "Salti di
   luce forti producono sfarfallio" (guida Higgsfield sui fotogrammi di inizio/fine); un grandangolo all'inizio e
   un teleobiettivo alla fine "confondono il modello". Il fotogramma finale serve a chiudere un movimento, non a
   cambiare scena. **Vedi il punto A della sezione 4.**
3. **Elenco delle cose che non cambiano** (il "contratto del primo fotogramma"): colore delle pietre, numero di
   pietre, metallo, numero di orecchini, mano e dito dell'anello, posizione della chiusura. Scritto in chiaro, con
   i numeri ("exactly two earrings, never three").
4. **Ordine del prompt**: fotogramma di partenza → cosa non cambia → una sola azione → camera → luce → divieti.
   Una scena, un'azione, un movimento di camera, uno stato finale. Lo stesso ordine lo indica la masterclass
   (sezione 5b): **la fedeltà va scritta per prima**, non in fondo. Il nostro `movimento.md` oggi la mette in fondo.
5. **Frasi di vincolo** che i tester usano: "One continuous shot", "locked tripod camera" (per i dettagli),
   "No cuts. No new objects. No text. No logos." Sono da provare, non garanzie.
6. **Un riferimento pulito, non un collage**: più immagini in conflitto peggiorano la coerenza.
7. **Clip corte = transizioni più pulite.** 4-5 secondi per scena; 10 s solo per cambiamenti grandi.
8. **Niente preset con effetti** (Morph, Melt, color grading, distorsioni): cambiano colore delle pietre e
   riflessi del metallo.
9. **Cambiare una cosa alla volta** tra un tentativo e l'altro (prompt, riferimento o durata) e annotarla.
10. **Controllare il file scaricato**: formato (un tester ha avuto un orizzontale con prompt verticale) e audio.

Sui modelli, solo opinioni di blog (nessun confronto serio): Seedance è indicato come più fedele al prodotto dal
primo all'ultimo fotogramma e migliore nella fisica (oggetti che si toccano, cadono, riflettono); Kling come
migliore sui movimenti delle persone. Per noi: **si parte con Kling 3.0 Standard** (economico, ha il fotogramma
finale e il multi-shot) e si prova Seedance 2.5 sulle scene di dettaglio se Kling deforma le pietre.

## 4. Cosa cambiare nello Studio

| | Cosa | Perché | Quando |
|---|---|---|---|
| **A** | "Finisci sulla foto vera" (`end_on_product`) solo se la scena **parte già dal gioiello in primo piano** con luce e distanza simili alla foto vera. Mai da una scena con la donna o in un altro luogo: lì la foto vera va come **inquadratura a sé, con stacco netto**. | Oggi lo Studio usa la foto vera del negozio come ultimo fotogramma anche dopo una scena AI in un altro luogo: è esattamente il "salto di luce e di ottica" che produce sfarfallio e deformazioni. | prima del test (regola al regista + controllo nel codice) |
| B | Nel prompt di movimento, l'elenco esplicito di cosa non cambia, con i numeri (pietre, orecchini, colori) presi dall'analisi del prodotto, **in testa al prompt**. | Contratto del primo fotogramma; masterclass: fedeltà prima dell'azione. | prima del test (`skills/_base/movimento.md` + campo nello storyboard) |
| B2 | `/mani-bancone`: niente scatolina che si apre né anello infilato al dito dall'AI. L'AI fa solo gesti semplici (mano che entra, si posa, si gira piano); il gesto di provarlo lo fanno le **clip vere** girate in negozio. | Le interazioni mani-oggetto sono il punto dove i video AI sbagliano di più (dita in più, anello che attraversa il dito). | prima del test (solo testo della skill) |
| H | **"Prova una scena"**: generare una sola inquadratura in 720p, col costo vero, prima di lanciare il Reel intero; registro automatico dei tentativi (tenuto / scartato / costo). | Bozza economica prima del definitivo; tasso di clip buone misurato dall'app, non a mano. | dopo il primo test riuscito |
| C | Aggiungere "One continuous shot, no cuts, no transitions." al blocco PRESERVE. | Kling a volte inserisce tagli. | prima del test (solo testo della skill) |
| D | Inquadrature di dettaglio con il gioiello a 2/3 del fotogramma; la donna a mezzo busto solo per il look, non per mostrare la pietra. | Deformazione dei pezzi piccoli. | prima del test (regola al regista) |
| E | Alzare la stima di riserva di Seedance 2.5 e tarare tutte le stime col primo `/estimate`. | Stima probabilmente bassa. | dopo il primo `/estimate` |
| F | Controllo qualità anche **sul video** (alcuni fotogrammi estratti confrontati con la foto vera), non solo sul fotogramma di partenza. | Le pietre si deformano durante il movimento, dopo il controllo. | dopo il test, se le deformazioni ci sono |
| G | Kling 4.0 (10 fotogrammi chiave) quando arriva nell'API. | Più controllo sui momenti chiave. | da ricontrollare a dicembre |

## 5. Le 7 funzioni del video di Gaito: servono a noi?

Video sponsorizzato da Higgsfield ([YouTube](https://www.youtube.com/watch?v=Rqq_ydRZsfY)). Sono tutte funzioni
del sito, da usare a mano, non dello Studio.

| Funzione | Per I Monili | Verdetto |
|---|---|---|
| Expand Image | Allargare una foto 4:5 in 9:16 senza tagliare il pezzo. Lo Studio lo fa già nel fotogramma chiave. | utile solo a mano, per una foto vera da mettere in una Storia |
| Color Grading | Rischia di cambiare il colore delle pietre: un'ametista deve restare quella vera. | **no** sul gioiello |
| Marketing Studio | Pubblicità generiche da foto o link prodotto: stile "UGC/ads" lontano dal nostro editoriale crema e serif. | no, al massimo per curiosità |
| Relight | Cambiare la luce di una foto vera: potrebbe avvicinare la foto vera del negozio alla luce della scena AI (punto A). | **da provare** a mano su una foto |
| Translation / lip-sync | Non facciamo video parlati. | no |
| Community | Vedere prompt e impostazioni dei video altrui che funzionano. | **sì**, come fonte di idee per prompt e movimenti |
| Seedance 2.0 da foto | È quello che fa già lo Studio (con Seedance 2.5 / Kling 3.0). | già coperto |

## 5b. Masterclass "da Zero a Pro in 1 ora" (Graphics LAB)

Anche questa sponsorizzata ([YouTube](https://www.youtube.com/watch?v=YobUWOD5qjw)). Riassunto di Hermes dalla
trascrizione (31/10), confrontato qui con lo Studio.

**Schemi di prompt** (la parte più riutilizzabile):
- immagine nuova: soggetto → testo esatto → luce → inquadratura → stile → vincoli;
- modifica di una foto: quale immagine → cosa cambiare → cosa conservare → vincoli;
- animazione: cosa resta fedele → azione e tempi → camera → audio → vincoli.

| Indicazione | Nello Studio | Da fare |
|---|---|---|
| Prima l'immagine giusta, poi l'animazione | già così: fotogramma con controllo qualità 8/10, poi video | niente |
| Non rimodificare la stessa immagine: gli artefatti si accumulano, ripartire dall'originale | già così: ogni tentativo riparte dalla foto vera (Image 1), mai dal tentativo precedente | niente |
| Fedeltà scritta per prima nel prompt di animazione | no: in `movimento.md` il PRESERVE è in fondo | punto B |
| Azioni semplici: mani + oggetti sbagliano | `/mani-bancone` chiede scatolina, anello infilato | punto B2 |
| Bozza economica prima del definitivo | c'è l'anteprima senza Higgsfield (zoom), non una bozza video vera | punto H |
| Testi e invito aggiunti in montaggio | già così: niente testo nel video | niente |
| Audio valutato a parte | già così: video muto, audio da Instagram | niente |
| Controllare il risultato (dettagli, oggetti che compaiono o spariscono) | controllo solo sul fotogramma di partenza | punto F |
| Modelli diversi per compiti diversi | immagini GPT-Image (fedeltà), video Kling/Seedance a scelta | provare Seedance sui dettagli se Kling deforma |
| Cartelle per progetto | già così: una cartella per Reel, collegata al pezzo | niente |

**Strumenti del sito** (Cinema Studio, Genjutsu, Canvas a nodi, 3D Jutsu, Edit Layers, Effects, Marketing
Studio): lavoro a mano, non automatizzabile dallo Studio. L'unico da tenere d'occhio è **Genjutsu (trasferimento
di movimento)**: in futuro potrebbe prendere il gesto da una clip vera girata in negozio e applicarlo a una scena,
ma con un gioiello piccolo il rischio di deformazione è alto. Non ora.

**MCP e API**: lo Studio usa già l'API (crediti a consumo dalla console). Higgsfield ha anche un MCP, collegato a
Claude su questo PC: utile per prove a mano da chat, ma scala crediti come l'API e non sostituisce lo Studio.
Da verificare se i crediti della console API e quelli dell'abbonamento al sito sono separati.

## 5c. Account, Unlimited e alternative (verificato il 31/10)

- **Account Higgsfield di Matteo**: piano gratuito, 10 crediti. GPT Image 2 (lo stesso modello che usa lo Studio
  via OpenRouter) c'è anche su Higgsfield e rientra nell'Unlimited, insieme a Nano Banana Pro/2, Seedream, Soul,
  FLUX.2. Ma **l'Unlimited vale solo a mano sul sito**: API, MCP e CLI scalano sempre crediti. Le immagini restano
  quindi nello Studio (stesso modello, ~0,10 € a fotogramma, controllo qualità automatico).
- **API Higgsfield**: prodotto separato dal sito, saldo in dollari a consumo, nessun abbonamento. Chiavi e
  ricariche su <https://console.higgsfield.ai> (l'aiuto Higgsfield la chiama anche open.higgsfield.ai). Ricarica
  minima 5 $, il saldo scade dopo un anno, lavori falliti o bloccati non addebitati, chiave mostrata una volta sola.
  Listino: Kling 3.0 0,112 $/s, Seedance 2.5 0,0738 $/s (prezzi di partenza).
  Reel con 3 scene AI da 5 s: circa 2,3 € con Kling e 1,8 € con Seedance se tutto riesce al primo colpo,
  circa 3 € con un tentativo in più per scena.
- **OpenArt** (valutata il 31/10): nessuna API pubblica documentata, solo MCP e CLI con login dal browser;
  costi per modello non pubblicati (si vedono solo con `openart model cost`); crediti mensili che **non passano al
  mese dopo**; uso commerciale solo dal piano Plus (34 $/mese). Con 1-2 Reel a settimana (~20 €/mese di video)
  un abbonamento mensile costa più dei crediti API Higgsfield, che durano 12 mesi. **Scartata per ora**; da
  rivalutare se il volume cresce molto (Natale) e solo dopo aver visto i costi veri per modello.

## 6. Protocollo per il test di oggi

0. **Bloccante**: nel `.env` del PC non c'è ancora la chiave Higgsfield (`HF_API_KEY_ID`, `HF_API_KEY_SECRET`):
   guida in `docs/reel-studio.md`. Comprare pochi crediti (scadono dopo 12 mesi).
1. Primo pezzo con **pietre grandi e colori netti** (non il gioiello più piccolo): se regge quello, si scende di
   dimensione.
2. **Una sola inquadratura** prima del Reel intero: Kling 3.0 Standard, 5 s, dettaglio, slow push-in, senza
   fotogramma finale. Annotare il costo vero dell'`/estimate` e quello addebitato.
3. Guardare la clip a velocità ridotta: numero e forma delle pietre, metallo, mani (dita), sfarfallio.
4. Una seconda prova cambiando **una sola cosa** (es. Seedance 2.5 al posto di Kling).
5. Solo allora il Reel completo (3-4 inquadrature).
6. Per ogni tentativo una riga: `n. / cosa ho cambiato / difetto visto / tengo o scarto / costo`. Alla fine:
   **tasso di clip buone** = clip usabili / clip generate. È il numero che dice quanto costa davvero un Reel.

---

## Fonti
- Video (sponsorizzati): [Raffaele Gaito, 7 funzionalità](https://www.youtube.com/watch?v=Rqq_ydRZsfY),
  [Graphics LAB, masterclass](https://www.youtube.com/watch?v=YobUWOD5qjw) (riassunto di Hermes dalla trascrizione)
- Ufficiali: [documentazione API Higgsfield](https://docs.higgsfield.ai/docs/models/video-generation.md)
  (Kling 3.0, Seedance 2.5, Seedance 2.0, Wan 3.0), [Kling 4.0 su Higgsfield](https://higgsfield.ai/blog/kling-4-0-on-higgsfield),
  [fotogrammi di inizio e fine](https://higgsfield.ai/blog/Kling-Start-End-Frames),
  [perché i crediti finiscono](https://higgsfield.ai/blog/why-ai-video-credits-run-out),
  [crediti spiegati](https://higgsfield.ai/blog/ai-video-credits-explained),
  [cosa consuma i crediti](https://higgsfield.ai/creator-hub/help-center/credits/what-uses-my-credits),
  [generazioni fallite](https://higgsfield.ai/creator-hub/help-center/troubleshooting/generation-is-stuck-or-failed),
  [guida Seedance 2.5](https://higgsfield.ai/blog/seedance-2-5-prompting-guide)
- Terzi: [Atlas Cloud, problemi Kling 4.0 Flash](https://www.atlascloud.ai/blog/tips/kling-4.0-flash-short-video-problems-fixes),
  [VEED, prompt Kling](https://www.veed.io/learn/kling-ai-prompting-guide),
  [Kling, video gioielli](https://kling.ai/topics/ai-jewelry-video),
  [ConnectionCafe, video prodotto coerenti](https://connectioncafe.com/product-videos-with-higgsfield/),
  [AdArena, Seedance 2.0 vs Kling 3.0](https://adarena.app/blog/seedance-2-0-vs-kling-3-0-2026-ai-video-showdown-brand-ads),
  [Yang's web, Veo vs Kling vs Seedance](https://www.yangsweb.com/blog/veo-vs-kling-vs-seedance-comparison-2026),
  [EvoLink, Kling 3.0 Turbo](https://evolink.ai/blog/kling-3-0-turbo-vs-kling-3-vs-o3),
  [Jewels Retouch, video gioielli con AI](https://jewelsretouch.com/blog/how-to-make-a-jewelry-ad-video-with-ai),
  [NemoVideo, meno generazioni sprecate](https://www.nemovideo.com/blog/higgsfield-pricing-editing-workflow)
