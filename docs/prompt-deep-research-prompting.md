# Super prompt — Deep Research: prompting per foto e video di gioielli e moda

Come usarlo: copia tutto ciò che sta sotto la riga "INIZIO PROMPT" in Claude Research, Gemini Deep Research, Perplexity o ChatGPT Deep Research. Lancialo su due strumenti diversi se puoi: dove concordano, il dato è più affidabile. Il risultato va in `nuove ricerche approfondite/` e poi viene fuso in `knowledge/fucina/`.

Prima di lanciarlo: sostituisci i segnaposto `[...]` nella sezione CONTESTO e controlla la sezione GIÀ NOTO.

---------- INIZIO PROMPT ----------

# RUOLO
Sei un ricercatore tecnico specializzato in generazione di immagini e video con AI per e-commerce di moda e gioielleria. Il tuo lavoro è produrre una guida operativa verificabile, non un riassunto di marketing.

# CONTESTO
Gestisco "I Monili Ravenna", negozio artigianale di Ravenna: bijoux in argento con pietre colorate, orecchini smaltati a fiore, giacche e gilet ricamati, borse in cuoio, abbigliamento boho-etnico. Genero foto e Reel su Higgsfield (piattaforma che ospita più modelli) partendo SEMPRE dalla foto reale del pezzo. Il gioiello e il capo reali non devono mai cambiare forma, colore, pietra, ricamo o proporzioni. Ho una testimonial fissa, "Aurora" (personaggio salvato su Higgsfield, descrizione fissa): stesso volto in tutti i contenuti, cambiano abiti, luoghi, pose e luce. Piano Higgsfield: [indicare piano e se uso Unlimited o crediti API]. Strumenti di lavoro: [Claude Code con MCP Higgsfield / interfaccia web].

# MODELLI DA COPRIRE
Seedream (versione più recente su Higgsfield), Nano Banana (Pro e 2), GPT Image (versione più recente), Seedance (versione più recente), Kling (versione più recente), Genjutsu (Motion Transfer). Per ciascuno indica la versione esatta che esiste oggi su Higgsfield e la data in cui l'hai verificata. Se un modello non è su Higgsfield, dillo e non scrivere di cosa non puoi confermare.

# GIÀ NOTO (non rifare, vai oltre)
Ho già tre ricerche generali su Higgsfield, moda e gioielli. Non ripetere: cos'è Higgsfield, panoramica dei modelli, consigli generici ("usa luce morbida", "descrivi il materiale"). Cerca solo ciò che manca. Se un'informazione generica è indispensabile per capire il resto, scrivila in una riga.

# LE 8 LACUNE DA COLMARE

1. ANELLI
   a) Foto studio su fondo avorio/crema: come si ottiene una prospettiva credibile, riflessi del metallo, pietra con taglio e colore fedeli, assenza di deformazioni del cerchio.
   b) Anello indossato su mano realistica: numero di dita corretto, unghie, pelle con grana, scala dell'anello rispetto al dito, proporzione pietra/dito. Errori tipici e correzioni.

2. GIACCHE E GILET RICAMATI
   Come mantenere fedeli: motivo del ricamo, colori dei fili, trama del tessuto, bottoni, cuciture, chiusure. Come evitare cartellini finti, loghi inventati, scritte illeggibili. Come evitare che il ricamo si "ripulisca" o si semplifichi. Capo indossato vs capo su appendino vs piatto.

3. ALTRI PEZZI: orecchini (a lobo e pendenti, smaltati a fiore), collane (lunghezza sul busto), bracciali (polso e avambraccio), borse in cuoio (scala rispetto al corpo, cuciture, fibbie). Per ciascuno: cosa fa perdere fedeltà, cosa fa sbagliare la scala, quale inquadratura funziona meglio.

4. SCHELETRO DEL PROMPT
   Proponi UN ordine dei blocchi valido per tutti i modelli (es. soggetto, riferimento da conservare, scena, luce, camera, vincoli negativi, formato). Spiega per ogni modello dove l'ordine conta davvero e dove si può cambiare. Dimmi se per alcuni modelli i "negative prompt" funzionano, vengono ignorati o peggiorano il risultato, con fonte.

5. PERSONAGGIO FISSO + PEZZO
   Come usare Aurora (personaggio salvato) insieme alla foto reale del pezzo senza che cambi il volto e senza che cambi il pezzo. Ordine e numero dei riferimenti, che cosa scrivere nel prompt per ognuno, come evitare che il gioiello prenda tratti del viso o che il volto "scivoli". Limiti noti (numero massimo di riferimenti, deriva dell'identità nelle serie).

6. GENJUTSU MOTION TRANSFER
   Cos'è, a cosa serve, come si usa passo per passo. Si può cambiare vestito e sfondo mantenendo il movimento? Cosa serve come ingresso (video di riferimento, immagine del personaggio), durata massima, costo, difetti tipici (mani, tessuti, gioielli che cambiano forma in movimento). Quando conviene rispetto a Seedance o Kling.

7. CREDITI E MCP
   Costi attuali per generazione di ogni modello (immagine e video, per secondo o per clip). Differenza tra Unlimited e API: cosa è davvero illimitato, su quali modelli, con quali limiti nascosti (coda, risoluzione, durata, uso commerciale). Cosa si può fare tramite MCP e cosa solo dall'interfaccia. Quale strada costa meno per fare 8 foto prodotto e 2 Reel a settimana.

8. GIUDIZIO DEL RISULTATO
   Per ogni tipo di pezzo (anello, orecchini, collana, bracciale, capo ricamato, borsa, foulard) una lista di difetti da cercare confrontando il risultato con la foto vera: forma, colore, numero di pietre, proporzioni, mani, ombre, riflessi, scritte, artefatti da AI. Per ogni difetto: come si vede, quanto è grave (da scartare / ritoccabile), come si corregge nel prompt.

# FORMATO DELLA RISPOSTA
Per OGNI modello (Seedream, Nano Banana, GPT Image, Seedance, Kling, Genjutsu):
- Versione e data di verifica.
- Prompt pronti da copiare, IN INGLESE, uno per ogni caso: anello su avorio, anello indossato, orecchini, collana, bracciale, gilet/giacca ricamati, borsa, Aurora + pezzo. Dove un caso non è adatto al modello, scrivi "non adatto" e perché.
- Tabella "errore → causa probabile → correzione nel prompt" (almeno 6 righe per modello).
- Un blocco "Cosa NON fare" (comportamenti confermati che peggiorano il risultato).
Poi una sezione finale unica: scheletro del prompt (punto 4), tabella difetti per tipo di pezzo (punto 8), tabella costi (punto 7).

# REGOLE SULLE FONTI (obbligatorie)
- Ogni affermazione porta URL e data di pubblicazione/ultimo aggiornamento della fonte.
- Etichetta OGNI affermazione con una sola di queste: TESTATO (risultato riproducibile mostrato con prompt e output), DOCUMENTAZIONE UFFICIALE (guida del produttore o di Higgsfield), MARKETING (blog o comunicato del produttore, promesse non verificate), OPINIONE (creator, forum, social).
- Preferisci fonti degli ultimi 90 giorni; segna come "possibile obsoleto" tutto ciò che è più vecchio, perché i modelli cambiano versione spesso.
- Se due fonti si contraddicono, riportale entrambe con l'etichetta e dì quale ti sembra più solida e perché.
- Se non trovi una fonte, scrivi "NON TROVATO". Non completare con supposizioni, non inventare parametri, nomi di funzioni o prezzi.
- Non copiare prompt da gallerie senza dire da dove vengono e se hanno davvero dato quel risultato.
- Non includere dati personali di terzi.

# CONTROLLO FINALE
Prima di consegnare, verifica: ogni prompt è in inglese e completo; ogni modello ha la sua tabella errori; ogni affermazione ha URL, data ed etichetta; le 8 lacune hanno tutte una risposta o un esplicito "NON TROVATO".

---------- FINE PROMPT ----------

## Note per Matteo (non incollare)
- Domanda aperta: aggiungere `knowledge/fucina/struttura-prompt.md` con lo scheletro dei 6 blocchi. Consiglio: sì, ma dopo la ricerca, così lo scheletro nasce dai dati (punto 4) e non da un'ipotesi.
- Quando torna il risultato: lo fondiamo in `knowledge/fucina/` con lo stesso metodo di oggi (modello per modello, ricette per categoria, tabelle difetti in `knowledge/valutazione/`).
