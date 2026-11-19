# Prompt A — Deep Research: modelli IMMAGINE (Seedream, Nano Banana, GPT Image)

Incolla tutto ciò che sta tra le righe INIZIO e FINE in Claude Research o Gemini Deep Research. Prima sostituisci il segnaposto `[...]`.

---------- INIZIO PROMPT ----------

# RUOLO
Sei un ricercatore tecnico specializzato in generazione di immagini con AI per e-commerce di moda e gioielleria. Devi produrre una guida operativa verificabile, non un riassunto di marketing.

# CONTESTO
Gestisco "I Monili Ravenna", negozio artigianale di Ravenna: bijoux in argento con pietre colorate, orecchini smaltati a fiore, giacche e gilet ricamati, borse in cuoio, abbigliamento boho-etnico. Genero foto su Higgsfield (piattaforma che ospita più modelli) partendo SEMPRE dalla foto reale del pezzo. Il pezzo reale non deve mai cambiare forma, colore, pietra, ricamo o proporzioni. Ho una testimonial fissa, "Aurora" (personaggio salvato su Higgsfield): stesso volto in tutte le foto, cambiano abiti, luoghi, pose e luce. Strumento di lavoro: [Claude Code con MCP Higgsfield / interfaccia web].

# MODELLI DA COPRIRE
Seedream, Nano Banana (Pro e 2), GPT Image: per ciascuno la versione esatta oggi disponibile su Higgsfield e la data in cui l'hai verificata. Se un modello non è su Higgsfield, dillo e non scrivere di ciò che non puoi confermare.

# GIÀ NOTO (non rifare)
Ho già ricerche generali su Higgsfield, moda e gioielli. Non ripetere cos'è Higgsfield, la panoramica dei modelli né consigli generici ("luce morbida", "descrivi il materiale"). Se un'informazione generica è indispensabile, una riga.

# LACUNE DA COLMARE

1. ANELLI
   a) Foto studio su fondo avorio/crema: prospettiva credibile, riflessi del metallo, pietra con taglio e colore fedeli, cerchio non deformato.
   b) Anello indossato su mano realistica: numero di dita corretto, unghie, pelle con grana, scala dell'anello sul dito, proporzione pietra/dito.

2. GIACCHE E GILET RICAMATI
   Come mantenere fedeli motivo del ricamo, colori dei fili, trama del tessuto, bottoni, cuciture, chiusure. Come evitare cartellini finti, loghi inventati, scritte illeggibili. Come evitare che il ricamo si semplifichi o si "ripulisca". Capo indossato vs su appendino vs piatto.

3. ALTRI PEZZI
   Orecchini (a lobo e pendenti, smaltati a fiore), collane (lunghezza sul busto), bracciali (polso e avambraccio), borse in cuoio (scala rispetto al corpo, cuciture, fibbie). Per ciascuno: cosa fa perdere fedeltà, cosa sbaglia la scala, quale inquadratura funziona meglio.

4. SCHELETRO DEL PROMPT (per immagini)
   Proponi UN ordine dei blocchi valido per tutti e tre i modelli (es. soggetto, riferimento da conservare, scena, luce, camera, vincoli, formato). Dì per ogni modello dove l'ordine conta davvero. Dì se i "negative prompt" funzionano, vengono ignorati o peggiorano il risultato, con fonte.

5. PERSONAGGIO FISSO + PEZZO
   Come usare Aurora insieme alla foto reale del pezzo senza che cambi il volto e senza che cambi il pezzo: ordine e numero dei riferimenti, cosa scrivere nel prompt per ognuno, come evitare che il gioiello prenda tratti del viso o che il volto "scivoli". Limiti noti (massimo di riferimenti, deriva dell'identità nelle serie).

6. GIUDIZIO DEL RISULTATO
   Per ogni tipo di pezzo (anello, orecchini, collana, bracciale, capo ricamato, borsa, foulard) una lista di difetti da cercare confrontando con la foto vera: forma, colore, numero di pietre, proporzioni, mani, ombre, riflessi, scritte, artefatti da AI. Per ogni difetto: come si vede, quanto è grave (da scartare / ritoccabile), come si corregge nel prompt.

# FORMATO DELLA RISPOSTA
Per OGNI modello:
- Versione e data di verifica.
- Prompt pronti da copiare, IN INGLESE, uno per caso: anello su avorio, anello indossato, orecchini, collana, bracciale, gilet/giacca ricamati, borsa, Aurora + pezzo. Dove un caso non è adatto, scrivi "non adatto" e perché.
- Tabella "errore → causa probabile → correzione nel prompt" (almeno 6 righe).
- Blocco "Cosa NON fare" (solo comportamenti confermati).
Poi una sezione finale unica: scheletro del prompt (punto 4) e tabella difetti per tipo di pezzo (punto 6).

# REGOLE SULLE FONTI (obbligatorie)
- Ogni affermazione porta URL e data di pubblicazione o ultimo aggiornamento.
- Etichetta OGNI affermazione con una sola di queste: TESTATO (risultato riproducibile con prompt e output mostrati), DOCUMENTAZIONE UFFICIALE (guida del produttore o di Higgsfield), MARKETING (blog o comunicato del produttore, promesse non verificate), OPINIONE (creator, forum, social).
- Preferisci fonti degli ultimi 90 giorni; segna "possibile obsoleto" ciò che è più vecchio.
- Se due fonti si contraddicono, riportale entrambe e dì quale sembra più solida e perché.
- Se non trovi una fonte, scrivi "NON TROVATO". Non inventare parametri, nomi di funzioni o prezzi.
- Non copiare prompt da gallerie senza dire da dove vengono e se hanno davvero dato quel risultato.

# CONTROLLO FINALE
Prima di consegnare verifica: ogni prompt è in inglese e completo; ogni modello ha la sua tabella errori; ogni affermazione ha URL, data ed etichetta; le 6 lacune hanno una risposta o un esplicito "NON TROVATO".

---------- FINE PROMPT ----------
