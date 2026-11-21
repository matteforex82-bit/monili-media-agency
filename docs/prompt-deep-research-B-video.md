# Prompt B — Deep Research: modelli VIDEO (Seedance, Kling, Genjutsu Motion Transfer)

Incolla tutto ciò che sta tra le righe INIZIO e FINE in Claude Research o Gemini Deep Research. Prima sostituisci il segnaposto `[...]`.

---------- INIZIO PROMPT ----------

# RUOLO
Sei un ricercatore tecnico specializzato in generazione di video con AI per e-commerce di moda e gioielleria. Devi produrre una guida operativa verificabile, non un riassunto di marketing.

# CONTESTO
Gestisco "I Monili Ravenna", negozio artigianale di Ravenna: bijoux in argento con pietre colorate, orecchini smaltati a fiore, giacche e gilet ricamati, borse in cuoio, abbigliamento boho-etnico. Genero Reel e Storie verticali su Higgsfield (piattaforma che ospita più modelli) partendo SEMPRE dalla foto reale del pezzo, che diventa il primo fotogramma o il riferimento del video. Il pezzo reale non deve cambiare forma, colore, pietra, ricamo o proporzioni durante il movimento. Ho una testimonial fissa, "Aurora" (personaggio salvato su Higgsfield): stesso volto in tutti i video, cambiano abiti, luoghi, pose e luce. Strumento di lavoro: [Claude Code con MCP Higgsfield / interfaccia web].

# MODELLI DA COPRIRE
Seedance, Kling, Genjutsu (Motion Transfer): per ciascuno la versione esatta oggi disponibile su Higgsfield e la data in cui l'hai verificata. Se un modello non è su Higgsfield, dillo e non scrivere di ciò che non puoi confermare.

# GIÀ NOTO (non rifare)
Ho già ricerche generali su Higgsfield, moda e gioielli. Non ripetere cos'è Higgsfield, la panoramica dei modelli né consigli generici ("movimento lento", "luce morbida"). Se un'informazione generica è indispensabile, una riga.

# LACUNE DA COLMARE

1. GENJUTSU MOTION TRANSFER
   Cos'è, a cosa serve, come si usa passo per passo. Si può cambiare vestito e sfondo mantenendo il movimento? Cosa serve in ingresso (video di riferimento, immagine del personaggio), durata massima, difetti tipici (mani, tessuti, gioielli che cambiano forma in movimento). Quando conviene rispetto a Seedance o Kling.

2. GIOIELLI E CAPI IN MOVIMENTO
   Per anelli, orecchini, collane, bracciali, giacche e gilet ricamati, borse: cosa si deforma o cambia durante il video (pietre che cambiano colore, ricamo che si scioglie, dita che si moltiplicano, catenine che si fondono), quali movimenti di camera e quali azioni del soggetto lo riducono (es. gesto lento, mano ferma, giro del polso), quale durata della clip regge meglio.

3. SCHELETRO DEL PROMPT (per video)
   Proponi UN ordine dei blocchi valido per i tre modelli (es. soggetto, riferimento da conservare, azione, camera, luce, durata, vincoli). Dì per ogni modello dove l'ordine conta davvero. Dì se i "negative prompt" funzionano, vengono ignorati o peggiorano il risultato, con fonte. Spiega come si scrive il movimento di camera e dell'azione in modo che il modello lo segua.

4. PERSONAGGIO FISSO + PEZZO IN VIDEO
   Come mantenere Aurora e il pezzo reale stabili per tutta la clip: ordine e numero dei riferimenti, primo/ultimo fotogramma, cosa scrivere nel prompt, come evitare che il volto o il gioiello cambino a metà video. Come concatenare più clip dello stesso personaggio senza deriva. Limiti noti.

5. GIUDIZIO DEL RISULTATO
   Per ogni tipo di pezzo una lista di difetti video da cercare confrontando con la foto vera (anche fotogramma per fotogramma): forma, colore, numero di pietre, proporzioni, mani, riflessi che sfarfallano, scritte, artefatti da AI. Per ogni difetto: come si vede, quanto è grave (da scartare / ritoccabile), come si corregge nel prompt o con una nuova generazione.

# FORMATO DELLA RISPOSTA
Per OGNI modello:
- Versione e data di verifica.
- Prompt pronti da copiare, IN INGLESE, uno per caso: anello in movimento, orecchini, collana, bracciale, gilet/giacca ricamati, borsa, Aurora + pezzo, giro di camera attorno al pezzo (turntable). Dove un caso non è adatto, scrivi "non adatto" e perché.
- Tabella "errore → causa probabile → correzione nel prompt" (almeno 6 righe).
- Blocco "Cosa NON fare" (solo comportamenti confermati).
Per Genjutsu: in più la procedura passo per passo e i casi d'uso consigliati.
Poi una sezione finale unica: scheletro del prompt (punto 3) e tabella difetti per tipo di pezzo (punto 5).

# REGOLE SULLE FONTI (obbligatorie)
- Ogni affermazione porta URL e data di pubblicazione o ultimo aggiornamento.
- Etichetta OGNI affermazione con una sola di queste: TESTATO (risultato riproducibile con prompt e output mostrati), DOCUMENTAZIONE UFFICIALE (guida del produttore o di Higgsfield), MARKETING (blog o comunicato del produttore, promesse non verificate), OPINIONE (creator, forum, social).
- Preferisci fonti degli ultimi 90 giorni; segna "possibile obsoleto" ciò che è più vecchio.
- Se due fonti si contraddicono, riportale entrambe e dì quale sembra più solida e perché.
- Se non trovi una fonte, scrivi "NON TROVATO". Non inventare parametri, nomi di funzioni o prezzi.
- Non copiare prompt da gallerie senza dire da dove vengono e se hanno davvero dato quel risultato.

# CONTROLLO FINALE
Prima di consegnare verifica: ogni prompt è in inglese e completo; ogni modello ha la sua tabella errori; ogni affermazione ha URL, data ed etichetta; le 5 lacune hanno una risposta o un esplicito "NON TROVATO".

---------- FINE PROMPT ----------
