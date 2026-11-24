# PRD operativo — Back-office fiscale: task per più agenti (bozza 24/11/2026)

Si legge insieme a `docs/prd-fiscale.md` (il perché e l'architettura) e a `docs/piano-sicurezza-vps.md` (messa in sicurezza della macchina). Questo file dice **cosa costruire, in che pezzi, con quali regole e come si controlla che sia fatto**, in modo che più agenti possano lavorare in parallelo senza pestarsi i piedi.

## 1. Regole che valgono per tutti gli agenti (non negoziabili)
1. **Solo dati finti.** Nessun dato reale, nessun file bancario, nessun estratto conto, nessuna fattura vera, nessun IBAN, nessun dato di clienti, né nel repository né nei prompt. I dati di prova si generano (`fixtures/`) e hanno nomi palesemente inventati.
2. **Niente sulla VPS e niente su servizi online** (Vercel, Neon, Google, banca, commercialista) senza un ok esplicito di Matteo per quel passo. Il codice si scrive e si prova **in locale** (Docker sul PC o su una macchina di prova).
3. **Nessun segreto nel repository.** Password, chiavi, token e indirizzi di posta reali vanno in variabili d'ambiente; nel repository solo file d'esempio (`.env.example`) con valori finti. I flussi n8n si esportano **senza credenziali**.
4. **Non toccare** `Pratiche Negozio/`, `.env`, `DashFinance/`, `ANALISI IVA/` e `finanze Matte 2026/` (si leggono, non si modificano: sono dati o progetti di Matteo). Per riusare un parser si copia la **logica** in un file nuovo, senza i dati.
5. **Ogni agente lavora su un proprio ramo** (nome `fiscale/<task>`) e sui **soli file della sua corsia** (§4). Niente commit su `master`, niente push: l'integrazione la fa Matteo.
6. **Ogni consegna ha test** che girano senza rete e senza chiavi, e un breve file `README` del pezzo con come si avvia e cosa non fa.
7. **I numeri fiscali sono stime.** Percentuali, aliquote e regole non si inventano: stanno in tabella `parametri` con valore, data di validità e fonte, e finché non le conferma il commercialista sono segnate «da confermare».
8. Rispondere e documentare **in italiano**. Il codice in inglese, i messaggi all'utente e i nomi dei flussi in italiano.
9. Se un compito richiede una decisione che non è scritta qui, **non indovinare**: scrivere la domanda nella sezione «Domande aperte» del proprio README e fermarsi su quel punto.

## 2. Convenzioni tecniche
- **Posizione nel repository:** `back-office/fiscale/` con le cartelle `db/` (migrazioni e viste), `ingest/` (lettura dei file), `n8n/` (flussi esportati), `infra/` (Docker, backup, accessi), `fixtures/` (dati finti), `tests/`, `docs/`.
- **Database:** Postgres 16. Importi in `numeric(12,2)`, date in `date`, orari in `timestamptz` con fuso `Europe/Rome`. Nomi di tabelle e colonne in italiano, minuscoli, con underscore. Migrazioni numerate e **ripetibili** (si possono rilanciare senza danni).
- **Parser:** Python 3.12, con test `pytest`. Ogni parser: file in ingresso → righe pulite + esito (`ok`, `da_verificare`, `rifiutato`) + motivo. Riconoscere i **duplicati** con l'impronta (hash) del file e delle righe.
- **Viste di calcolo:** i calcoli stanno in viste SQL (nessuna formula nella dashboard). Ogni vista ha un test con dati finti e il risultato atteso scritto a mano.
- **Flussi n8n:** un flusso = un file JSON esportato senza credenziali + un README (ingressi, uscite, cosa fa se fallisce). Ogni invio di posta ha **un destinatario fisso da variabile** e una modalità «prova» che scrive su file invece di inviare.
- **Nessun IBAN completo:** solo gli ultimi 4 caratteri se serve distinguere i conti.

## 3. Modello dati di partenza (da non discostarsene senza chiedere)
| Tabella | Campi principali |
| --- | --- |
| `conti` | id, nome (es. «Conto negozio 21»), titolare, ultime4, attivo |
| `movimenti` | id, conto_id, data, descrizione, importo (negativo = uscita), categoria_id, stato_classificazione, importazione_id, impronta |
| `categorie` | id, nome, tipo (`azienda`, `famiglia`, `privata`, `da_verificare`) |
| `regole_classificazione` | id, testo_da_cercare, conto_id (opz.), categoria_id, priorità, attiva |
| `corrispettivi_mensili` | id, sede (`17`, `21`), anno, mese, lordo, fonte (`manuale`, `foto`, `pdf`), allegato_path, controllato |
| `scadenze` | id, tipo (`iva`, `f24`, `acconto`, `inps`, `camera_commercio`, `altro`), descrizione, data, importo_stimato, importo_reale, stato (`da_pagare`, `pagata`), nota |
| `accantonamenti` | id, scadenza_id, data, importo, nota |
| `fatture_estere` | id, fornitore, importo, valuta, ricevuta_il, termine_invio, inviata_il, stato (`da_inviare`, `inviata`, `scaduta`), file_path |
| `comunicazioni_iva` | id, ricevuta_il, oggetto, scadenza_risposta, stato (`da_rispondere`, `risposta`, `archiviata`), file_path, nota |
| `parametri` | chiave, valore, valido_dal, fonte, stato (`da_confermare`, `confermato`) |
| `importazioni` | id, tipo, nome_file, impronta, esito, motivo, data |
**Viste attese:** `v_spese_mensili`, `v_drenaggio_liquidita` (uscite non aziendali per conto e mese), `v_iva_stimata`, `v_accantonamento_dovuto`, `v_liquidita_libera`, `v_scadenze_prossime`, `v_fatture_estere_in_ritardo`.
**Formula di accantonamento (parametri, non numeri nel codice):** `rapporto = iva_versata_anno_precedente / corrispettivi_lordi_anno_precedente` (per mese o trimestre); `dovuto_mese = lordo_mese × rapporto × (1 + margine_prudenziale)`; quando c'è `importo_reale` di una scadenza, sostituisce la stima e si calcola la differenza.

## 4. Corsie (chi tocca cosa) e dipendenze
| Corsia | File di sua proprietà | Può partire subito? |
| --- | --- | --- |
| **A. Database** | `back-office/fiscale/db/` | Sì |
| **B. Lettura file (ingest)** | `back-office/fiscale/ingest/`, `fixtures/` | Sì |
| **C. Flussi n8n** | `back-office/fiscale/n8n/` | Dopo A1 (tabelle) per i test, la bozza no |
| **D. Infrastruttura** | `back-office/fiscale/infra/` | In locale sì; sulla macchina vera no |
| **E. Dashboard** | `back-office/fiscale/dashboard/` | Dopo A2 (viste) |
| **F. Regole fiscali e domande** | `back-office/fiscale/docs/` | Sì |
Due agenti non scrivono mai nella stessa corsia nello stesso momento.

## 5. I task

### Corsia A — Database
**A1. Schema e migrazioni.** Creare le tabelle del §3 con vincoli (chiavi, controlli sugli stati, importi), indici utili e migrazioni numerate ripetibili. *Uscita:* `db/migrations/*.sql`, `db/README.md`. *Accettazione:* su un Postgres 16 vuoto in Docker le migrazioni si applicano due volte di fila senza errori; un test controlla che i vincoli rifiutino valori non validi (stato inesistente, importo nullo).
**A2. Viste di calcolo.** Scrivere le viste del §3, con la formula di accantonamento letta dalla tabella `parametri`. *Accettazione:* test con dati finti e risultati attesi scritti a mano (almeno: un mese con tutte le categorie, un mese senza corrispettivi, una scadenza con importo reale che sostituisce la stima). Nessuna formula con numeri scritti nel codice. *Dipende da:* A1.
**A3. Dati finti e test SQL.** `fixtures/` con almeno 12 mesi di movimenti, corrispettivi e scadenze inventati, e uno script che li carica. *Accettazione:* da zero a database popolato con un solo comando; le viste restituiscono valori coerenti. *Dipende da:* A1.

### Corsia B — Lettura dei file
**B1. Parser CSV bancario.** Un parser con **mappatura configurabile delle colonne** (data, descrizione, importo, segno, separatore, formato data, decimali), perché il formato esatto delle banche di Matteo non è noto. Produce righe pulite, riconosce i **duplicati** (impronta) e segnala le righe malformate. *Accettazione:* test con tre file finti in formati diversi (virgola e punto e virgola, importi con segno e con colonne dare/avere); rilanciare lo stesso file non duplica nulla.
**B2. Motore di classificazione.** Applica `regole_classificazione` ai movimenti (priorità, per conto, testo contenuto) e lascia `da_verificare` ciò che non riconosce. *Accettazione:* test su casi ambigui (due regole che si sovrappongono, descrizione vuota); non cambia mai una classificazione fatta a mano.
**B3. Lettura e controllo dei corrispettivi.** Riadattare la **logica** del confronto tra totale calcolato e totale ufficiale già usata in `ANALISI IVA` (leggere il codice, non i dati). Input: i due totali mensili per sede, inseriti a mano o letti da un PDF finto. **Se il totale non torna il caricamento è `da_verificare` e non entra nei conti.** *Accettazione:* test con un PDF o un testo finto che torna, uno che non torna, uno in due file.
**B4. Estrazione dei dati di una fattura estera (facoltativo, Fase 2).** Solo la struttura: da file allegato a registro (fornitore, importo, data) con **conferma umana obbligatoria**. Nessun servizio esterno senza ok di Matteo.

### Corsia C — Flussi n8n (si scrive e si prova in locale; l'installazione sulla macchina vera è un passo separato con ok)
**C1. Fattura estera.** Modulo (nome fornitore, importo, valuta, data di ricezione, foto o PDF) → salva il file nell'archivio → scrive in `fatture_estere` con `termine_invio` = ricezione + N giorni (N da `parametri`, **valore «da confermare»**) → invia la mail al destinatario fisso con l'allegato → segna `inviata` → un flusso giornaliero avvisa se il termine si avvicina (`v_fatture_estere_in_ritardo`). *Accettazione:* in modalità «prova» il flusso scrive su file la mail con l'allegato e il registro è aggiornato; un caso con termine scaduto genera l'avviso.
**C2. Import bancario.** Quando un CSV arriva in una cartella o da un modulo, lancia il parser B1 e il motore B2, scrive in `movimenti` e `importazioni`, e produce un riepilogo con le righe `da_verificare`. *Accettazione:* lo stesso file due volte non duplica; un file malformato viene rifiutato con il motivo.
**C3. Scadenze e accantonamento.** Ogni giorno legge `v_scadenze_prossime` e `v_accantonamento_dovuto` e manda a Matteo un avviso con «quanto mettere via». Ogni settimana manda a Mirca il riepilogo (scadenze, cosa mettere via, spese da controllare) **senza importi dei singoli movimenti**. *Accettazione:* in modalità «prova» i messaggi finiscono su file e rispecchiano i dati finti.
**C4. Corrispettivi mensili.** Modulo con i due totali (negozio 17, negozio 21) e foto allegata; richiama B3; promemoria mensile a Matteo. *Accettazione:* totale che non torna → segnalato, non registrato.
**C5. Comunicazioni IVA (Fase 2).** Registro con scadenza di risposta, promemoria e archivio degli allegati.
**C6. Promemoria di manutenzione.** Aggiornamenti di sicurezza da riavviare, verifica del backup, controllo dello spazio disco.

### Corsia D — Infrastruttura (in locale finché Matteo non dà l'ok)
**D1. Docker Compose di prova.** Postgres **nuovo e separato** (rete propria, in ascolto solo su `127.0.0.1`), Metabase, volume per i dati. *Accettazione:* parte con un comando sul PC; nessuna porta pubblicata su `0.0.0.0`; utente di sola lettura per la dashboard e utente di scrittura per i flussi.
**D2. Backup cifrati e ripristino.** Script di copia cifrata giornaliera (`pg_dump` + cifratura) e **prova di ripristino automatica su un database vuoto**. *Accettazione:* dopo il ripristino le viste danno gli stessi numeri; la chiave di cifratura non è nel repository.
**D3. Accesso dalla rete privata.** Documento con la configurazione di Tailscale (ACL solo sui dispositivi di Matteo) e come aprire Metabase e i moduli dal telefono. Nessuna modifica alla macchina senza ok.
**D4. Messa in sicurezza della VPS.** Si esegue **come da `docs/piano-sicurezza-vps.md`**, un passo alla volta, con Matteo, **non da un agente da solo**. Bloccante prima di qualsiasi dato reale.

### Corsia E — Dashboard
**E1. Schede di Metabase.** Elenco delle domande (SQL sulle viste, in sola lettura) e degli schermi: «spese per conto, categoria e mese», «quanto drena la liquidità del negozio», «scadenze e cosa mettere via», «fatture estere da inviare». *Accettazione:* ogni scheda è una query documentata su una vista; esportazione riproducibile. *Dipende da:* A2, D1.

### Corsia F — Regole fiscali e domande
**F1. Questionario per il commercialista.** Una pagina con le domande del PRD (termine per le fatture estere, regime IVA, scadenze dell'anno, comunicazioni IVA, formato e indirizzo di invio, margine prudenziale consigliato, riepiloghi 2025). *Accettazione:* domande chiuse e brevi, da girare per WhatsApp o email.
**F2. Tabella dei parametri.** Elenco dei parametri con valore provvisorio, fonte e stato `da_confermare`. Nessun valore preso dalla memoria dell'agente.
**F3. Calcolo del rapporto di partenza dal 2025 (solo in locale sul PC di Matteo, con dati veri).** Script che legge i riepiloghi veri **da un percorso fuori dal repository** e stampa il rapporto per mese e trimestre. Non salva dati né output nel repository. *Si fa dopo* i test con dati finti e con Matteo presente.
**F4. Test di accettazione completo con dati finti** (vedi §7).

## 6. Ordine di lavoro (ondate)
| Ondata | Task | Condizione |
| --- | --- | --- |
| **1** (in parallelo, senza macchina né dati veri) | A1, B1, B3, D1, F1, F2 | Nessuna |
| **2** | A2, A3, B2, C1 (bozza), C3 (bozza), D2 | A1 finito |
| **3** | C2, C4, E1, D3 | A2, B1, B3, D1 finiti |
| **4** (con Matteo) | D4 (sicurezza della VPS), poi installazione sulla macchina e prova con dati finti | Ondate 1-3 finite e **ok di Matteo** |
| **5** (con Matteo, dati veri) | F3, primo import reale, parametri confermati dal commercialista | D4 completo, backup provato, **ok di Matteo** |
Fase 2 (B4, C5, Paperless-ngx e corrispettivi giornalieri) solo dopo l'ondata 5.

## 7. Come si controlla che è fatto
- **Per ogni task:** i test del task passano senza rete, i file sono solo nella corsia dell'agente, il README del pezzo è scritto (cosa fa, cosa non fa, domande aperte), nessun segreto o dato reale (si controlla con una ricerca di indirizzi di posta, numeri lunghi e parole come «password» prima di consegnare).
- **Test di accettazione finale (F4), con dati finti:** da database vuoto → migrazioni → caricamento dei dati finti → import di un CSV bancario finto (anche due volte) → inserimento dei corrispettivi di un mese → viste con i risultati attesi → flusso fattura estera in modalità «prova» con mail su file → riepilogo per Mirca su file → backup e ripristino con gli stessi numeri.
- **Porte dell'integrazione:** (G1) infrastruttura sicura (D4 fatto); (G2) tutto provato con dati finti (F4 verde); (G3) primo dato reale solo dopo l'ok di Matteo e con backup provato.

## 8. Come lanciare gli agenti (promemoria per Matteo)
- Un agente per corsia, al massimo tre in parallelo, ognuno con il testo di questo file e del suo task come istruzione, e con il divieto di toccare la VPS e i dati reali.
- Ogni agente consegna un ramo `fiscale/<task>` con test verdi e README; l'integrazione e la revisione sono tue (o di un agente di revisione separato, che non ha scritto il codice).
- Per decisioni non scritte qui (formato delle banche, termine fatture estere, margine, destinatari) gli agenti si fermano e le scrivono nelle domande aperte.
