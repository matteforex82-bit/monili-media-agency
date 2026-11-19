## Conoscenza: Seedream (foto da foto vera; Higgsfield `seedream_5_0_flash`, 5.0 Lite, 5.0 Pro `seedream_v5_pro`)
Etichette: [verificato] = visto nei test di Matteo; [fonte] = dalla ricerca (report 13/11 rivisto), non ancora provato; [ipotesi].

**Come ragiona**
- Pensa la scena prima di disegnarla. Non ha negative prompt, guidance né seed (su Lite): i divieti si scrivono dentro il prompt come frasi ("no jeans, no jewelry, no bag"). [fonte: report 13/11] I divieti scritti così sono nei prompt di prova, esito ancora in corso. [ipotesi]
- Scrivere "9:16" o "4K" nel testo non serve: formato e risoluzione si impostano nei parametri. [fonte: report 13/11]
- Lunghezza: un brief ordinato di circa 50-150 parole; sotto 10 parole decide lui, oltre 600 perde dettagli. [fonte: report 13/11; le 50-150 non verificate]
- Ordine che funziona meglio: uso/tipo di foto, soggetto con materiali esatti, azione, ambiente, luce, camera, eventuale testo tra virgolette. [fonte: report 13/11]
- Fino a 10 immagini di riferimento. [fonte: report 13/11, catalogo Higgsfield]

**Tenere il pezzo identico**
- Aprire con la frase che blocca: "Keep the exact piece from the reference: shape, proportions, stones, enamel colours, metal finish." [verificato: 10/11, anello bijoux, voto 4,5]
- Una sola modifica per turno, ripetendo ogni volta cosa non deve cambiare. Il drift cresce se chiedi più cose insieme. [fonte: report 13/11; Playbook 13/11]
- Ogni immagine allegata ha un ruolo scritto ("Image 1: the real garment. Image 3: face and hair only."). Mai citare immagini non allegate ("image 4"): il modello le ignora o inventa. [verificato: 16/11, errore visto]
- Il solo riferimento visivo non basta per un capo: va descritto a parole (tessuto, colori, motivo, collo, zip, orlo). [verificato: 16/11, giacca reinterpretata senza descrizione: base quasi nera, fiori tondi, capo troppo lungo]
- Se nel prompt descrivi un capo diverso da quello delle foto, vince la descrizione: con tre foto di una giacca a quadri marrone e la descrizione di una giacca verde ricamata, Seedream 5.0 lite ha disegnato la giacca verde. La descrizione deve essere del pezzo vero, scritta guardando le sue foto. [verificato: 18/11, prova di Matteo]
- Il testo scritto nell'immagine esce solo se lo chiedi: parole esatte tra virgolette, e senza "No text" nel prompt. Seedream 5.0 Pro, Flash e 5.5 scrivono bene il testo in più lingue; per la Lite non è documentato. Controllare ogni lettera e gli accenti. [fonte: report 13/11; prova con "No text": nessun testo, come previsto]
- Foto intera, frontale e nitida del capo come riferimento, non solo dettagli piccoli. [verificato: 16/11, stessa prova]
- Descrivere materiali veri ("sterling silver", "velvet", "sherpa"), mai aggettivi vuoti ("8k", "masterpiece", "hyperrealistic"). [fonte: report 13/11; Playbook]

**Volti e persone**
- Con un frame di un video di terzi tra i riferimenti, il volto della modella si diluisce: tenere 3 riferimenti (volto, corpo, capo). Se serve la posa di un frame, scrivere "use only pose and framing, ignore her face, clothes, background". [verificato: 16/11]
- Un riferimento della modella a figura intera già vestita ricopia i suoi vestiti (jeans, maglietta): usare una foto con solo volto e capelli. [verificato: 16/11]
- Per volti, schede personaggio e modifiche con volto il catalogo Higgsfield indica Seedream 5.0 Pro. [fonte: catalogo Higgsfield]

**Risultati reali**
- Anello bijoux 14 €, Seedream 5.0 Flash 2k 3:4: identico (6 pannelli di smalto, colori, oro), fondo studio, ombra realistica, 0,5 crediti. [verificato: 10/11, voti 4,5]
- Stesso anello con GPT Image 2.6: anello piccolo, colori e texture ridisegnati, 880x1168: Seedream meglio. [verificato: 10/11]
- Foto da camera ritoccata: Seedream resta fedele, FLUX ricompone e inventa oggetti. [verificato: 10/11]
- Giacca con foto in negozio (cartellini, sfondo): prima va ripulita con UNA modifica ("replace only the background, remove the price tags") e poi controllato che non compaia un cartellino ricostruito. [fonte: Playbook 13/11; il cartellino fantasma è stato visto il 10/11, verificato]

**Costi e controllo**: una foto circa 0,5 crediti. Controllare a 100%: dita, gioielli, pietre, motivo del capo; chi guarda ridotto non vede questi difetti. [verificato: 10/11 e 16/11]
**Da verificare [dubbio]**: Seedream 5.5 con fondo trasparente e 100 modifiche in fila (3,5 crediti a 2K); "Example-Based Editing" (coppia prima/dopo applicata a nuovi pezzi, utile per il fondo avorio); 5.0 Pro a 2,5 e Lite a 1 credito.
Per approfondire: `Learn Higgsfield/docs/Prompting Avanzato Gioielleria e Moda.md` (sezione Seedream), `PROMPT_PLAYBOOK.md` (J1, A0, A1), `GENJUTSU_PROVE_E_RICETTA.md` (sezione 2 e 4).
