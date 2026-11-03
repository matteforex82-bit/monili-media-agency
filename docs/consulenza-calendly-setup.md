# Consulenza gratuita: configurazione di Calendly e testi pronti

Riferimento: `brainstorming marketing strategie.md` §7 (J06 e J07). Qui c'è solo cosa impostare nell'account Calendly Free e cosa copiare nelle chat. **Il sito non mostra nulla della consulenza finché non inserisci il link reale** (vedi «Accendere la consulenza sul sito»). Controlla le funzioni nel tuo account: le condizioni del piano gratuito possono cambiare.

## 1. Impostazioni dell'evento (un solo tipo di appuntamento)
| Impostazione | Valore |
|---|---|
| Nome | Consulenza gratuita in videochiamata |
| Durata pubblica | 10 minuti |
| Preparazione (non visibile alla cliente) | 5 minuti, nel tuo calendario |
| Anticipo minimo | 3 ore |
| Fuso orario | Europe/Rome |
| Disponibilità | Quattro momenti separati a settimana, **negli orari in cui sei davvero in negozio** (decidili tu: non sono nel codice) |
| Calendario collegato | Il tuo, per evitare doppie prenotazioni |
| Account per la cliente | Non richiesto |
| Cancellazione e spostamento | Dal link personale ricevuto; il nuovo orario rispetta le 3 ore di anticipo |

## 2. Domande del modulo (non ripeterle sul sito)
1. Nome ed e-mail (obbligatori, standard di Calendly).
2. **Numero WhatsApp** (obbligatorio). Nota nel campo: «Ti chiamiamo noi su WhatsApp: deve essere un numero raggiungibile su WhatsApp».
3. Acquisto: «Per me» / «Un regalo».
4. Categoria cercata: bijoux, borse e accessori, abbigliamento, **non so**.
5. Budget indicativo: fasce, con **non so**.
6. Quando ti serve: data o «nessuna urgenza».
7. Pezzo già visto (facoltativo): riferimento o link alla scheda.

Non chiedere altro: niente dati sanitari, niente indirizzo (l'indirizzo si raccoglie solo se si passa a un ordine).

## 3. Prima di accendere il link
- [ ] Prenota tu stesso uno slot di prova da telefono e controlla: orario, fuso, e-mail di conferma, link personale di annullamento.
- [ ] Prenota sotto le 3 ore e uno slot occupato: devono essere rifiutati.
- [ ] Sposta e annulla dal link personale: il calendario si aggiorna.
- [ ] Verifica che il tuo WhatsApp (375 771 3966) possa fare videochiamate dal telefono e dal PC.
- [ ] Rileggi `/privacy`: con il link acceso compare il paragrafo su Calendly (generato dal sito). Se Calendly cambia fornitore o regione dei dati, va aggiornato.

## 4. Accendere la consulenza sul sito
1. In Vercel, progetto `monili-vetrina`, Settings → Environment Variables: aggiungi `NEXT_PUBLIC_CONSULTATION_BOOKING_URL` con il link pubblico dell'evento (deve essere `https://calendly.com/...`).
2. Ripubblica (redeploy). Compaiono: voce «Consulenza» nel menu, pagina `/consulenza`, seconda slide della Home, riga nella sitemap, paragrafi su Calendly in privacy e cookie.
3. Per spegnerla: togli la variabile e ripubblica.

## 5. Messaggi manuali (WhatsApp, dal numero centrale)
Segnati l'appuntamento nel registro privato (scadenze e promemoria), mai nello Studio.

**Conferma personale (dopo la prenotazione)**
> Ciao [nome], sono [tu] di I Monili. Ti confermo la consulenza di [giorno] alle [ora]: ti chiamo io in videochiamata su WhatsApp da questo numero (375 771 3966). Se ti serve cambiare orario puoi usare il link nell'e-mail di conferma. A presto!

**Promemoria (poco prima)**
> Ciao [nome], tra poco ti chiamo su WhatsApp per la consulenza delle [ora]. Se non puoi, nessun problema: dal link dell'e-mail puoi spostarla.

**Cliente assente: un solo tentativo, un solo messaggio, nessuna penale**
> Ciao [nome], ti ho chiamata alle [ora] ma non sono riuscito a sentirti. Nessun problema: puoi prenotare un altro orario da qui [link], oppure scriverci quando vuoi.

**Dopo la call senza acquisto**
> Grazie del tempo, [nome]! Se cambi idea o vuoi vedere altro, scrivici quando vuoi.

(Nessun riepilogo né sollecito commerciale dopo una consulenza conclusa senza acquisto: PRD §7.3.)

Se la cliente decide di acquistare si passa al riepilogo del modello B di `docs/impegni-legali.md`, **dopo la verifica del pezzo in negozio** (PRD §8).
