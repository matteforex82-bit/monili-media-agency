# PRD — Back-office del negozio (bozza 24/11/2026)

Stato (24/11/2026): **Modulo A (consulenze) costruito e provato con due prenotazioni di prova**, codice in `back-office/` (la copia viva è nel progetto Apps Script del foglio, sull'account del negozio). **Modulo B (buoni) non iniziato.** Mancano privacy aggiornata, cancellazione su Calendly e le prove elencate in `back-office/README.md`. Non annunciare ai clienti servizi o buoni finché non sono collaudati (vedi `brainstorming marketing strategie.md`, J08–J11).

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

## 5. Modulo B — Buoni con scadenza
**Foglio «Buoni».** Colonne: codice · importo · data emissione · scadenza · saldo · stato (attivo, usato, scaduto) · numero WhatsApp (opzionale, solo se la cliente accetta il promemoria) · note.
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
- Se Calendly Free consente webhook o solo lettura del calendario (da verificare nell'account).
