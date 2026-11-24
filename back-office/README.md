# Back-office del negozio

Strumenti privati del negozio, **separati dallo Studio e dal sito**. Non contengono dati di clienti: i dati vivono in Google (foglio e Calendario dell'account del negozio). PRD: `docs/prd-back-office.md`.

## Consulenze da 15 minuti (attivo dal 24/11/2026)
- **Cosa fa:** legge il Google Calendar del negozio, scrive/aggiorna il foglio «Consulenze», imposta i promemoria a 2 ore e 1 ora, segna «annullata» se la cliente annulla, cancella dopo un mese la riga e l'evento del Calendario.
- **Dove gira davvero:** nel progetto **Apps Script legato al foglio «Appuntamenti Consulenza 2026»**, sull'account Google del negozio (cartella Drive «Calendly Consulenze»). Il progetto si chiama ancora «Untitled project»; il trigger `syncConsulenze` va ogni 5 minuti.
- **Questo repository ha solo una copia:** `apps-script/consulenze.gs`. **La copia viva è quella su Google.** Se si cambia il codice qui bisogna incollarlo di nuovo in Apps Script (Estensioni → Apps Script → sostituire tutto → salvare); se si cambia lì, aggiornare qui.
- **Reinstallare da zero:** aprire il foglio → Estensioni → Apps Script → incollare `consulenze.gs` → eseguire `syncConsulenze` (concedere i permessi) → eseguire `installaTrigger`.
- **Costi:** nessuno (Apps Script, Calendario e Fogli gratuiti; Calendly Free; videochiamata sul WhatsApp del 21).

### Formato reale degli eventi Calendly (prova del 24/11/2026)
- Titolo `<nome cliente> and I Monili Ravenna`, luogo = numero della cliente (comincia con «+»: la cella del foglio va in formato testo e non si usa `appendRow`, altrimenti `#ERROR!`).
- Descrizione: nome evento, luogo, domanda facoltativa seguita dalla risposta («Per favore, condividi tutto ciò che può essere utile per preparare il nostro incontro.: …»), poi i link per annullare e spostare. Se la cliente non scrive nulla la domanda non ha risposta e la nota resta vuota (provato sul testo con uno script di prova, non ancora con una prenotazione reale senza commento).
- Se si cambia il testo della domanda in Calendly, aggiornare `CONFIG.QUESTION_TEXT` nello script.

### Limiti e cose non fatte
- La cancellazione dopo un mese riguarda riga del foglio ed evento del Calendario. **La prenotazione su Calendly resta**: verificare se il piano Free cancella da solo, altrimenti a mano.
- La cancellazione degli eventi vecchi non è stata provata (serve un evento di più di un mese; per provarla si può abbassare `RETENTION_DAYS` su un evento di prova).
- I promemoria valgono per il calendario del negozio. Chi lo riceve condiviso (Mirca, telefono del negozio) imposta le notifiche a 2 ore e 1 ora nelle impostazioni del proprio account.
- Avvisi WhatsApp automatici allo staff: non attivi (servirebbero le API Business, a pagamento). Per ora basta la notifica dell'app Calendario.
- `/privacy` non cita ancora il passaggio dei dati nel foglio e nel Calendario (Google): da aggiornare prima dell'uso con clienti vere.
- Il foglio ha l'account del negozio come unico proprietario: verifica in due passaggi, nessuna condivisione via link.
