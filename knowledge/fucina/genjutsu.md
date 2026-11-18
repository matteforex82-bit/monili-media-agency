## Conoscenza: Genjutsu (Higgsfield, video da un altro video)
Etichette: [verificato] = visto nei test di Matteo; [fonte] = ricerca, non ancora provato; [ipotesi].
Cos'è: non crea video da zero, rifà un video esistente (4-30 s). Tre usi: Motion Transfer (prende solo movimento, tempi e camera e ricostruisce persona, abiti e scena dalle immagini), Object Swap (cambia un solo elemento), Restyle. [fonte: report 13/11]

**Cosa funziona**
- Motion Transfer, clip da 14 s a 480p, tre riferimenti (due frame con la giacca e il volto della modella): volto molto buono e coerente, giacca fedele, movimento fluido. [verificato: 16/11, esito parziale]
- Il Lite sostituisce il capo e il soggetto ma tiene lo sfondo del video, non quello dell'immagine. Sul video di strada: giacca fedele, cammino credibile, voti 4 e 3,5. [verificato: 10/11, prove 9 e 10]

**Cosa NON rifare**
- Object Swap per cambiare l'identità di una persona: due prove, il volto resta quello originale. [verificato: 15/11 e 16/11]
- Style: ridisegna tutto il video in uno stile. [verificato: 14-15/11]
- Motion Transfer senza riferimenti di gambe e scarpe: inventa una gamba bianca e una scarpa in più; senza foto del retro inventa il retro del capo. Serve una foto intera già vestita, con pantaloni e stivali. [verificato: 16/11]
- Clip con il telefono davanti al viso o con più persone: il volto non si legge. Clip di 4-5 s, un solo taglio, volto frontale nel primo fotogramma. [verificato: 16/11; scelta del clip: ricetta v0 da validare]
- Prove lunghe: 14 s costano molto; provare a 480p e 4-5 s (Lite 4 crediti; Objects swap Standard 4 s = 12 crediti). [verificato: 10/11 e 16/11]
- `replace_object` costava 63 crediti: fuori budget. [verificato: 10/11]

**Prompt di movimento (ricetta v0, da validare)**: "The person in the video is replaced by the character in image 1, wearing exactly the outfit shown in image 1. Keep the motion, pacing and camera of the video. One person only, both legs wear the same trousers and boots, no white clothing, no sneakers." [fonte: GENJUTSU_PROVE_E_RICETTA.md, non ancora validata]
- Occlusioni rapide, piccoli loghi, bracciali e fibbie danno artefatti. [fonte: report 13/11]
- Video di terzi: solo prova privata; serve il consenso scritto prima di pubblicare e il contenuto va dichiarato AI. [regola del progetto]

Per approfondire: `Learn Higgsfield/GENJUTSU_PROVE_E_RICETTA.md` (registro prove e "da non rifare"), `costi_test.csv` (prove 9 e 10).
