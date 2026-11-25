# PRD — Back-office del negozio (bozza 24/11/2026)

Stato (24/11/2026): **Modulo A (consulenze) costruito e provato con due prenotazioni di prova**, codice in `back-office/` (la copia viva è nel progetto Apps Script del foglio, sull'account del negozio). **Modulo B (buoni): deciso il 24/11 con Mirca (cartacei a mano in negozio, digitali sul sito con registro nostro, §5), non ancora costruito.** Mancano privacy aggiornata, cancellazione su Calendly e le prove elencate in `back-office/README.md`. Non annunciare ai clienti servizi o buoni finché non sono collaudati (vedi `brainstorming marketing strategie.md`, J08–J11).

## 1. Obiettivo
Un posto privato, separato da Studio e sito, dove il negozio tiene le cose operative e riceve gli avvisi giusti. Prima fase: **consulenze da 15 minuti** e **buoni con scadenza**. Le fasi successive (riserve, burocrazia, fatture, contabilità, commercialista) si aggiungono solo quando le prime due funzionano.

## 2. Confini (decisioni già prese)
- **Separato dallo Studio e dal database pubblico del sito.** Nello Studio, nei prompt e nel catalogo non entrano dati di clienti (`docs/impegni-legali.md`, PRD §16.3).
- **Nessun messaggio automatico alle clienti.** I promemoria arrivano a Matteo e alle commesse. Il messaggio WhatsApp alla cliente lo invia una persona, da un link già compilato (decisione 24/11/2026). Le API WhatsApp Business sono rimandate: costo, modelli approvati da Meta, consenso scritto.
- **Nessuna promessa di disponibilità e nessuna riserva automatica.**
- **Numero WhatsApp unico del negozio:** 375 771 3966.

## 3. Dove vivono i dati
Fase 1: un Foglio Google **privato** sull'account del negozio, con verifica in due passaggi, condiviso solo con Matteo e le commesse. Automazioni con Google Apps Script (gratis) o n8n (da scegliere in fase di costruzione; n8n in cloud sarebbe un ulteriore trattamento di dati da dichiarare in privacy).
Alternative valutate: database gratuito su Vercel (il piano Hobby è non commerciale, da verificare; vedi voce «Vercel Pro» in `docs/interventi-richiesti-matteo.md`) e database sul PC (le commesse non lo vedono). Se in futuro serve di più, si migra con esportazione del foglio.

## 4. Modulo A — Consulenza da 15 minuti
**Flusso.** La cliente prenota su Calendly Free → l'appuntamento compare nel Google Calendar del negozio con nome e numero WhatsApp → uno script legge il calendario e aggiorna il foglio «Consulenze» → avviso a Matteo e alle commesse 30 minuti prima.
- Niente webhook di Calendly (probabile piano a pagamento, da verificare): si legge il calendario.
- **Formato reale dell'evento (prova del 24/11/2026):** titolo «<nome cliente> and I Monili Ravenna»; luogo = numero di telefono della cliente; la cliente compare tra gli ospiti con l'e-mail; la descrizione contiene solo nome evento, luogo e i link per annullare e spostare; promemoria 30 minuti prima già impostato; organizzatore = account del negozio. **Le risposte alle domande personalizzate non arrivano nell'evento**: il foglio non le avrà (se servono, si guardano su Calendly).
- **Durata:** annunciata come 15 minuti; sul calendario la fascia è di 30 per lasciare margine se la cliente vuole parlare di altro (decisione di Matteo, 24/11/2026). La cliente nella conferma vede la fascia da 30.
- **Chi chiama:** chiama il negozio, su WhatsApp, al numero lasciato dalla cliente.
- Colonne «Consulenze»: data e ora · nome · WhatsApp · link per annullare/spostare · stato (prenotata, fatta, annullata, non presentata) · data di cancellazione. L'e-mail della cliente non si copia nel foglio.
- **Conservazione:** un mese dalla fine del contatto, poi cancellazione automatica della riga (decisione 24/11/2026; chiude la voce «chi cancella» per le consulenze).
- **Promemoria:** 2 ore e 1 ora prima (decisione 24/11/2026), impostati dallo script sull'evento. Valgono per il calendario del negozio; chi riceve il calendario condiviso deve attivare le stesse notifiche nelle impostazioni del proprio account.
- **Cancellazione:** oltre alla riga del foglio, lo script cancella dal Calendario gli eventi Calendly finiti da un mese. Resta da cancellare a parte la prenotazione su Calendly (verificare se il piano Free ha la cancellazione dati automatica; altrimenti a mano).
- **Avviso (richiesta di Matteo, 24/11/2026):** sul telefono di **Mirca** e sul **telefono del negozio**, su WhatsApp. WhatsApp automatico verso lo staff richiede le API Business di Meta (costo per messaggio e modello approvato, da verificare) o un servizio terzo: va scelto prima di costruire. Soluzione gratuita già pronta: condividere il calendario del negozio con gli account Google dei due telefoni e usare la notifica dell'app Calendario (30 minuti prima, già impostata). Decidere se basta o se si aggiunge WhatsApp.
- **Verifiche:** prenotazione di prova compare nel foglio; spostamento e annullo aggiornano lo stato; l'avviso arriva 30 minuti prima a chi deve; la riga sparisce a un mese (test con data accorciata).
- **Da allineare:** `brainstorming marketing strategie.md` dice ancora dieci minuti; `docs/consulenza-calendly-setup.md` ha il vecchio link e non cita la fascia da 30.

## 5. Modulo B — Buoni (decisione di Matteo e Mirca, 24/11/2026)
**Due circuiti separati, che non si parlano:**
- **B1 — Buoni cartacei del negozio.** Restano com'erano: li gestiscono le commesse a mano, in autonomia. **Fuori dal back-office e da questo PRD**: nessun registro, nessun codice, nessuna verifica del sistema. Per evitare confusione, un buono cartaceo non si può usare per un codice digitale e viceversa (se la cliente presenta l'uno, si controlla l'uno).
- **B2 — Buoni digitali sul sito.** Li vende il sito (pagina «Regala un buono»), li registriamo noi in un database privato e li inviamo in formato digitale con un **codice univoco**. Tutto il resto di questa sezione riguarda B2. Le regole commerciali sono in `brainstorming marketing strategie.md` §10 (importo libero, scadenza un mese, negozio emittente 17 o 21, al portatore, uso parziale con saldo, Natale 2026 fino al 25/1/2027).

**Responsabilità (decisione 25/11/2026):** il negozio risponde solo del buon funzionamento del flusso online (B2). Come le commesse gestiscono i buoni cartacei, e gli errori che possono fare, non è compito del sistema.

**Un buono vale in un solo negozio.** Il 17 e il 21 hanno buoni distinti, ciascuno spendibile soltanto nel negozio che lo ha emesso. Chi vuole spendere in entrambi compra due buoni (uno per negozio, con codici diversi). Sul sito si sceglie il negozio prima di pagare e il negozio è scritto sul buono e nel registro. Per ora non esiste un buono «valido in tutti e due».

### B2 — Flusso
1. **Acquisto** sul sito: negozio (17 o 21), importo libero, nome ed e-mail/WhatsApp di chi compra, destinatario e messaggio breve (facoltativi), scelta di come ricevere il buono: **digitale** oppure **ritiro in negozio** (nel negozio emittente). Casella delle condizioni di vendita con recesso a 14 giorni (§16 del brainstorming).
2. **Pagamento** con uno di **tre metodi** (decisione 25/11/2026): **bonifico istantaneo** (due IBAN diversi, quello del negozio scelto), **link SumUp** (unico per entrambi i negozi) o **Satispay** (due link, uno per negozio, perché i due negozi hanno account separati). Il sito mostra solo l'IBAN o il link del negozio scelto, tranne SumUp che è unico. Il buono nasce **«in attesa»**: nessun credito finché il pagamento non risulta incassato, verificato da Matteo. Con SumUp l'incasso non indica il negozio: vale il negozio scelto nella richiesta, e si controlla importo e riferimento. Il sito non memorizza IBAN o link dentro il registro: sono configurazione del sito.
3. **Attivazione e consegna** da parte di Matteo: verificato il pagamento, il buono passa ad «attivo», si genera il codice (vedi sotto) e **Matteo lo invia** a chi ha comprato (e-mail o WhatsApp dal numero del 21), con codice, QR, negozio, scadenza. Se la cliente ha scelto il ritiro, si concorda il ritiro nel negozio emittente (versione stampata con lo stesso codice del registro; la cliente la ritira e firma/conferma il ritiro). Nessun invio automatico.
4. **Uso al banco**, solo nel negozio emittente, da una pagina da telefono con accesso autenticato (staff): si inserisce o scansiona il codice → il sistema mostra negozio, scadenza, stato, saldo → la commessa conferma l'importo → il saldo si aggiorna e resta il movimento.
5. **Scadenza:** a un mese dall'emissione (data esplicita); promemoria semi-manuale come sotto.

### B2 — Regole del codice e del registro (da §10.2 del brainstorming)
- Codice **non prevedibile**: 12 caratteri casuali da un alfabeto senza caratteri ambigui (niente 0/O, 1/I/L), generati con un generatore crittografico, con prefisso `MD-` per distinguerli dai buoni cartacei. Mai sequenziali.
- Il PDF e il QR **non sono prova di validità**: contano solo il codice e il saldo nel registro. Copie dello stesso buono rimandano allo stesso credito.
- **Nessun doppio addebito**: l'uso è una sola operazione che controlla e scala il saldo insieme (blocco/transazione), con un identificativo per ritentativo; saldo mai negativo.
- Stati: in attesa, attivo, usato, scaduto, **annullato/rimborsato** (recesso).
- Tabelle: **Buoni** (codice, negozio, valore iniziale, saldo, emissione, scadenza, stato, e-mail di chi compra, e-mail/WhatsApp destinatario se dato, riferimento pagamento) e **Movimenti** (codice, data, importo, tipo, chi). Il saldo si calcola dai movimenti.
- **Nessuna pagina pubblica** mostra o modifica il registro. Il sito pubblico può solo creare la richiesta «in attesa»; non legge mai codici o saldi.
- Dati di clienti: mai nello Studio né nel catalogo pubblico.

### B2 — Dove vive il database (da decidere prima di costruire)
Il PRD §16.3 del brainstorming esclude il database pubblico del sito. Due strade, da scegliere:
- **a) Foglio Google privato + Apps Script** (come le consulenze, gratis, le commesse lo vedono già). Il blocco `LockService` evita i doppi addebiti; va bene per il volume di un negozio. Il modulo del sito invia la richiesta a uno script.
- **b) Piccolo database separato** (Postgres/Neon in un progetto distinto dal catalogo, o la VPS quando sarà messa in sicurezza, `docs/piano-sicurezza-vps.md`) con una pagina autenticata per le commesse. Più robusto, ma più lavoro e un fornitore in più da dichiarare in `/privacy`.
**Raccomandazione (25/11/2026): partire da (a)**, collaudo con dati finti; migrare a (b) solo se il volume cresce, servono login personali o il foglio diventa scomodo da telefono. Per rendere facile la migrazione: due schede «Buoni» e «Movimenti» con una riga per dato, date AAAA-MM-GG, importi numerici, codice come chiave mai modificata, movimenti solo aggiunti (le correzioni sono movimenti di rettifica), logica solo nello script (le commesse non toccano le celle) e sito/pagina d'uso che parlano con lo script, non con il foglio.

### B2 — Cosa non si fa
- Non si annunciano né si vendono buoni digitali finché registro e prova al banco non sono collaudati e il consulente non ha risposto su IVA e validità (voce 13). Fino ad allora la pagina «Regala un buono» non è linkata dal sito.
- Nessun invio automatico di buoni o messaggi: li invia Matteo dopo aver verificato il pagamento.
- Nessun buono valido in entrambi i negozi: servono due buoni.
- Non si integra l'uso del buono con acquisti online sul sito (non concordato).

### B2 — Verifiche (collaudo con dati finti)
Richiesta «in attesa» non dà credito; attivazione genera codice unico e invia l'e-mail; uso parziale scala il saldo e lascia lo storico; due usi contemporanei dello stesso buono: uno solo passa; buono scaduto, annullato o del negozio sbagliato rifiutato; codice inesistente rifiutato senza rivelare nulla; la vista «in scadenza» mostra il buono giusto e il link `wa.me` ha il testo corretto.

### Dettaglio colonne e promemoria (bozza precedente, vale per B2)
**Foglio «Buoni».** Colonne (aggiungere: negozio 17/21 · consegna digitale/ritiro · metodo di pagamento bonifico/SumUp/Satispay · riferimento del pagamento): codice · importo · data emissione · scadenza · saldo · stato (attivo, usato, scaduto) · numero WhatsApp (opzionale, solo se la cliente accetta il promemoria) · note.
**Foglio «Movimenti buono».** Una riga per ogni uso o rettifica: codice · data · importo scalato · chi lo ha registrato. Il saldo si calcola dai movimenti, mai a mano, per avere uno storico affidabile.
**Uso al banco.** Pagina semplice da telefono, con accesso Google limitato: «emetti buono» e «usa buono». Al primo collaudo basta il foglio stesso.
**Promemoria di scadenza (semi-manuale).** Ogni mattina la vista «Buoni in scadenza» mostra i buoni che scadono entro N giorni (N da decidere con il consulente) con un link `wa.me` già compilato. Il testo di esempio vive in `docs/messaggi-ordine-pronti.md`. Una persona preme invio dal numero del 21.
- **Cose che non si decidono qui:** durata e regole della scadenza, trattamento fiscale (buono monouso o multiuso) e testo da pubblicare nelle condizioni. Aspettano il parere del consulente (J11). Fino ad allora lo strumento si costruisce e si prova, ma i buoni digitali non si annunciano.
- **Verifiche:** emissione e uso aggiornano saldo e storico; un buono scaduto non si può usare; la vista in scadenza mostra il buono giusto e il link apre WhatsApp con il testo corretto; un uso doppio dello stesso buono viene rifiutato.

## 6. Dashboard (risposta alla domanda di Matteo)
Sì, ma per gradi, senza costruire in anticipo.
1. **Fase 1:** una scheda «Oggi» nel foglio: consulenze di oggi, buoni in scadenza, cose da fare. Basta e costa niente.
2. **Fase 2:** una pagina web privata con login (Apps Script o app piccola), solo se le commesse la usano ogni giorno e il foglio diventa scomodo.
3. **Fase 3:** moduli aggiuntivi (riserve J08, venduto → archivia sul sito, riepilogo del lunedì J14), ognuno con il suo PRD breve.

## 7. Burocrazia, fatture, contabilità (fasi successive, nessun impegno ora)
Il back-office **non sostituisce** gli strumenti fiscali. Fatture elettroniche, registratore telematico e contabilità restano a commercialista e strumenti già in uso. Il back-office raccoglie e prepara: esportazione mensile di incassi e buoni, elenco scadenze (con avviso), cartella dei documenti. Prima di ogni invio automatico verso il commercialista serve sapere quali formati e quali dati accetta, e aggiornare `/privacy`.

## 8. Privacy (da fare prima dell'uso reale)
- Aggiornare `/privacy` (vetrina: `src/lib/legal-content.ts`): dati trattati (nome, WhatsApp, buono), finalità, conservazione (consulenze un mese; buoni secondo il consulente), fornitore (Google; più eventuale n8n).
- Account del foglio con verifica in due passaggi, accesso solo allo staff, nessuna condivisione via link pubblico.
- Backup: esportazione periodica del foglio in una cartella privata.
- Nessun dato di clienti nei messaggi inviati ai servizi AI.

## 9. Ordine di lavoro
1. Matteo: crea il foglio privato sull'account del negozio e lo condivide con l'AI solo se serve il collaudo (o fornisce un foglio di prova senza dati reali).
2. Matteo: J05 (WhatsApp del 21) e J06 (Calendly con 15 minuti e domande), da cui dipende il Modulo A.
3. AI: struttura dei fogli, scheda «Oggi», script del Modulo A, collaudo con dati finti.
4. AI: Modulo B con dati finti. Matteo: parere del consulente su scadenza e fisco prima dell'uso reale.
5. Aggiornamento `/privacy`, poi uso reale.

## 10. Aperte
- Canale degli avvisi (email o Telegram) e chi li riceve.
- Giorni di preavviso della scadenza del buono e durata del buono (consulente).
- Se serve già in fase 1 l'accesso delle commesse da telefono.
- Buoni digitali: dove vive il database (foglio o database separato, §5), **Deciso il 25/11/2026: foglio Google.** Pagamenti: bonifico istantaneo (2 IBAN), SumUp (link unico), Satispay (2 link, account separati già esistenti). Da definire: come ricollegare ogni incasso a una richiesta (riferimento da far scrivere nella causale o nella nota, soprattutto con SumUp, dove il negozio non risulta).
- Se Calendly Free consente webhook o solo lettura del calendario (da verificare nell'account).
