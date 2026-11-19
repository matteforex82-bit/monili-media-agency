## Struttura del prompt per le foto (Seedream, Nano Banana, GPT Image)
Etichette: [fonte: ricerca A 19/11] = dai test e dalle guide, non ancora provato da noi; [ipotesi]; [verificato]. I prompt sono sempre in inglese. Per i video (Seedance, Kling, Genjutsu) lo scheletro è in fondo, dalla ricerca B del 19/11. Questo file non entra ancora nei prompt dello Studio: è una guida per chi scrive a mano.

**Sei blocchi, sempre in questo ordine** [fonte: ricerca A 19/11]
1. Intento e soggetto, con il ruolo di ogni riferimento: "Real commercial macro photograph of the exact ring from Image 1" / "@Aurora wearing the piece from Image 2".
2. Il pezzo da non cambiare (Product Lock): forma, numero di pietre, griffe, bottoni, taglio, colore vero, finitura del metallo, rilievo del ricamo, cuciture, fibbie. Misure in mm o cm dove le hai.
3. Posa, contatto e scala: dove sta sul corpo (anulare, lobo, cm sotto le clavicole, sull'anca), ombra di contatto, niente che copra il pezzo.
4. Scena e sfondo, in positivo: "matte warm ivory stone, pale cream seamless backdrop", mai lasciare vuoti da riempire.
5. Luce e materiali, scritti separati: sorgente e direzione ("soft light from camera-left"), poi finitura del metallo, smalto, grana del tessuto o della pelle.
6. Inquadratura, ottica e chiusura: il taglio ("cropped just below the knuckles", volto almeno il 25% del quadro), 85mm o macro 2:1, "keep unchanged", e una sola frase corta di esclusioni concrete ("no hang tags, no logos, no text").
Fuori dal prompt, nei controlli di Higgsfield: formato (1:1, 3:4, 4:5), risoluzione, qualità, Complexity o Thinking, sfondo opaco o trasparente. Scriverli nel testo non serve.

**Dove l'ordine conta davvero**
- Nano Banana: i primi dettagli pesano di più, quindi blocchi 1 e 2 in apertura. Divieti in positivo.
- Seedream: frasi naturali compiute, 60-150 parole, sotto le 600; riferimenti chiamati Image 1 / Image 2; modifica e "Keep unchanged" separate.
- GPT Image: va bene anche a sezioni (Subject / Scene / Details / Constraints), ma "cambia solo X" e i vincoli restano separati; con il ritocco a pennello l'immagine da correggere è sempre Image 1.

**Negative prompt**: nessuno dei tre ha un campo dedicato. Gli elenchi alla Stable Diffusion ("ugly, deformed, extra fingers") sono ignorati o peggiorano. Le fonti si contraddicono sulle esclusioni in prosa: Google dice solo divieti in positivo, OpenAI, ByteDance e un test indipendente dicono che una frase corta funziona nella maggior parte dei casi ma ogni tanto compare testo. Sintesi: scena e luce in positivo nei blocchi 4-5, una sola frase corta di esclusioni nel blocco 6, e controllo a occhio. [fonte: ricerca A 19/11]

**Quale modello per quale pezzo** (la ricerca; quando un nostro test dice altro, vince il test)
- Seedream 5.5: Aurora + pezzo, anello indossato, pelle e tessuti, capi boho scoperti, pose spontanee, modifiche in serie. Seedream 5.0 Pro: packshot con più oggetti. [fonte: test Runware e On-Model 12/11] Anello da studio con Flash: voto 4,5 nel nostro test del 10/11. [verificato]
- GPT Image 2.6 Sunburst: giacche e gilet ricamati, bottoni esatti, macro di borse. Evitare capi scollati (filtro). [fonte: test Higgsfield 05/11, On-Model]
- Nano Banana Pro: 4K, 4:5 nativo, HEX, @Elements (collane, orecchini pendenti, Aurora). Nano Banana 2: non per anelli né ricami. [fonte: Masonry, On-Model]
- Pezzo che resta sbagliato dopo 2-3 tentativi: tenere scena e modella dell'AI e rimettere in post-produzione i pixel veri della foto originale. [fonte: guida OpenAI, Masonry]

**Controllo**: zoom 100% accanto alla foto vera, giudicare prima il pezzo e poi l'estetica; se cambia un elemento che identifica il pezzo (pietre, griffe, motivo, bottoni, manici, colore), si scarta. Difetti per tipo di pezzo: `knowledge/valutazione/`. [fonte: ricerca A 19/11]

## Struttura del prompt per i video (Seedance 2.5, Kling 4.0, Genjutsu)
Sempre in inglese. [fonte: ricerca B 19/11, guide ufficiali Seedance e Kling; non ancora provato da noi sui nostri pezzi]

**Sette blocchi** (cambia soprattutto l'ultimo, per modello)
1. Formato e regola generale: "One continuous 5-second shot with no cuts", 9:16 (anche nel parametro), una sola sorgente di luce.
2. Riferimenti attivi: @Image1, @Image2, @Video1 nell'ordine di caricamento, un solo compito stretto per file e cosa ignorare. Più viste dello stesso pezzo: "one single ring, only one in the video".
3. Soggetto e blocco del pezzo: quante persone ("EXACT 1 HUMAN CHARACTER"), 2-3 dettagli che non cambiano (metallo, numero di pietre o griffe, colori dello smalto, ricamo, manici e fibbie). Con la foto di partenza non si descrive di nuovo ciò che si vede: si dichiara cosa resta uguale.
4. Primo fotogramma e mappa del luogo: pezzo nel terzo centrale, punti fissi ("frame-left", "frame-right"), pareti lisce senza scritte.
5. Azione a finestre di secondi interi (0-3s:, 3-6s:): una sola azione, dallo stato iniziale allo stato finale, senza "fast".
6. Camera e ottica: un solo movimento con parole fisiche ("locked camera", "slow push-in of 5 cm", "25-degree front arc"), legato a un evento ("as the light reaches the stone"); focale e profondità di campo.
7. Audio e vincoli: Seedance, suono vero tra frasi semplici e toggle Audio spento; Kling, solo "No subtitles. No background music."; Genjutsu, blocchi POSITIVE LOCKS e una riga "Avoid:".

**Dove l'ordine conta**
- Seedance: l'ordine dei file caricati (immagini e video contano insieme) decide chi entra per primo; stile e riferimenti in testa, continuità e vincoli in coda.
- Kling: apertura "One continuous shot", ruoli @ImageN prima dei tempi, tempi allineati all'ordine dei keyframe.
- Genjutsu: l'ordine delle foto fissa @Image1, @Image2; dire cosa si sostituisce e cosa resta di @Video1.

**Divieti**: nessun campo negative prompt. Kling: solo positivo, tranne sottotitoli e musica. Seedance: 3-5 vincoli concreti in coda, l'audio si spegne dal toggle. Genjutsu: "Avoid:" breve e specifica per il compositing. [fonte: ricerca B 19/11]

**Quale modello per quale pezzo** (nessun test nostro sui gioielli di Matteo: tutto da provare)
- Anelli, orecchini, collane, bracciali: Seedance 2.5 dalla foto (bozza in Flash), Kling 4.0 per confronto. Genjutsu no.
- Gilet e giacche ricamati: Seedance 2.5 con la foto indossata; Genjutsu Object Swap solo con un capo "controfigura" nel video.
- Borsa: Seedance (slider lento) o Kling 4.0 con 4 keyframe; Genjutsu con una borsa di forma simile in mano.
- Aurora + pezzo: still approvato e poi animato; Omni Reference con @Aurora; se Seedance rifiuta il volto, Kling 4.0.
Esempi per ogni pezzo: `prompt-video-esempi.md`. Difetti da cercare nel video: `knowledge/valutazione/valutazione-video.md`.
