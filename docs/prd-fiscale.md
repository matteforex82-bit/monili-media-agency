# PRD — Back-office fiscale privato del negozio (bozza 24/11/2026)

Stato: **solo progettazione, nulla installato né costruito.** Non è stato toccato niente sulla VPS, né DashFinance, né dati reali o file bancari. Il PRD delle consulenze e dei buoni è a parte: `docs/prd-back-office.md`. **I task per più agenti, con corsie, ondate e criteri di accettazione, sono in `docs/prd-fiscale-task.md`.** Sicurezza della macchina: `docs/piano-sicurezza-vps.md`.

## 1. Decisione
Una soluzione **autonoma sulla VPS privata di Matteo**, che continua a funzionare anche senza l'abbonamento a Claude. Claude serve per **costruirla e mantenerla** (script, query, flussi n8n) e, se Matteo vuole, per analizzare dati ripuliti. **Nessun flusso quotidiano dipende da Claude.**
- Chi la usa: **Matteo**, da PC e telefono, tramite **Tailscale** (rete privata). **Mirca** (la titolare) non ha accesso: riceve un riepilogo (email o WhatsApp).
- È separata dallo Studio, dal sito e dal back-office delle consulenze. Nessun dato di clienti dentro. Niente IBAN completi.
- **Non è contabilità ufficiale:** liquidazioni, F24 e dichiarazioni restano al commercialista. Le cifre sono stime da validare con lui.
- DashFinance (`C:\Users\matte\Desktop\PROGETTI AI\DashFinance`: React + Firebase, circa 2.200 righe, nessun test, modello pensato per la famiglia) **non si riusa**: si riparte da zero, prendendo solo le idee (timeline delle scadenze, schede riassuntive). Non si tocca né si cancella.

## 2. Problemi da risolvere (parole di Matteo, 24/11/2026)
1. Scaricare i **report della banca**, metterli in un posto sicuro e avere una dashboard che li macina per una **fotografia delle spese**: conti di Mirca e del negozio 21, spese private e di famiglia che drenano liquidità.
2. Inviare i **documenti al commercialista**: Mirca gli dà una fattura estera, lui fa una foto col telefono e parte un flusso che manda la mail al commercialista con il documento, **entro N giorni** (il valore esatto va chiesto al commercialista).
3. **Comunicazioni IVA** a cui rispondere: cosa è arrivato, scadenza della risposta, documenti.
4. **Scadenze IVA e F24 e mettere via i soldi in anticipo.**
5. Altre cose che emergeranno: l'architettura deve poterle accogliere.

## 3. Cosa si fissa ora e cosa si può cambiare
- **Si fissa ora (costoso da cambiare):** i dati in **Postgres** sulla VPS con backup cifrati; i documenti in un archivio sulla VPS; **n8n** come unico esecutore dei flussi (importazioni, invii, avvisi). Schema dei dati e flussi sono la parte che dura.
- **Si può cambiare dopo:** la schermata (dashboard, moduli). Se parla solo con Postgres e n8n, si sostituisce senza rifare niente.

## 4. Architettura (strumenti open source da installare; candidati da verificare, non provati)
- **Rete e sicurezza:** nessuna porta pubblica; si entra solo da Tailscale (ACL solo sui dispositivi di Matteo). Postgres in ascolto solo in locale. Aggiornamenti regolari. **Backup cifrati giornalieri fuori dalla VPS** e prova periodica di ripristino. Registro degli accessi.
- **Dati:** Postgres. Tabelle di partenza: conti, movimenti (da CSV), categorie e regole, scadenze fiscali, accantonamenti, fatture estere (ricezione, termine, stato, file, invio), comunicazioni IVA (arrivo, scadenza di risposta, stato, allegati), corrispettivi mensili per sede.
- **Documenti:** cartella cifrata sulla VPS; candidato **Paperless-ngx** (archivio con ricerca e riconoscimento del testo) dalla Fase 2.
- **Dashboard «fotografia delle spese»:** candidato **Metabase** (o Grafana) collegato a Postgres in sola lettura: spese per conto, categoria e mese; quota privata e di famiglia che drena la liquidità; accantonamenti e scadenze. Raggiungibile da PC e telefono tramite Tailscale.
- **Flussi (n8n):**
  1. *Fattura estera:* modulo con foto (si apre dal telefono via Tailscale) → salva nell'archivio, registra data e termine, **invia la mail al commercialista con l'allegato**, segna «inviata», avvisa se il termine si avvicina.
  2. *Import banca:* quando Matteo carica il CSV, lo legge, classifica con le regole, segnala le righe «da verificare».
  3. *Scadenze e accantonamento:* controllo giornaliero, calcolo di **quanto mettere via**, avviso a Matteo; **riepilogo settimanale a Mirca**.
  4. *Comunicazioni IVA:* registro con scadenza di risposta e promemoria.
- **Mail:** invio da un indirizzo del negozio (casella `info@imoniliravenna.it` su Aruba, ancora da creare, voce 19 di `docs/interventi-richiesti-matteo.md`; alternativa: altro SMTP), con elenco fisso dei destinatari (il commercialista) per non sbagliare indirizzo.
- **Telegram:** un bot richiede un indirizzo pubblico per ricevere i messaggi; con la sola rete Tailscale non basta. Per la foto dal telefono si parte quindi dal **modulo web di n8n** dentro Tailscale.
- **Claude:** costruisce e mantiene script e flussi; analisi su richiesta con dati ripuliti (Matteo decide cosa mostrarmi: ciò che leggo in chat viene elaborato da Anthropic). Facoltativa una vista Artifact sul computer (da provare con dati finti).
- **Mantenimento:** è un impegno vero (aggiornamenti, backup, prove di ripristino). Si mettono promemoria periodici gestiti da n8n.

## 5. Dove si fanno i calcoli (la dashboard non calcola nulla)
Quattro strati; i calcoli stanno **dentro Postgres**, in viste SQL scritte nel repository e coperte da test:
1. **Dati grezzi:** il file così com'è (CSV banca, foto o PDF dei corrispettivi) nell'archivio, con data e origine. Non si modifica mai.
2. **Lettura e pulizia (n8n + script Python sulla VPS):** per i corrispettivi si riadatta il parser già scritto in `ANALISI IVA` (confronta il totale calcolato con il totale ufficiale). **Se il totale non torna, il caricamento viene segnalato e non entra nei conti.** I duplicati si riconoscono.
3. **Calcoli (viste SQL):** classificazione dei movimenti con la tabella delle regole; spese per conto, categoria e mese; IVA a debito stimata; accantonamento necessario per ogni scadenza; **liquidità libera = saldo reale − accantonamenti**. Con poche migliaia di righe all'anno le viste si calcolano all'istante: il dato nuovo compare appena è scritto. Se in futuro serve velocità, viste materializzate aggiornate da n8n dopo ogni importazione.
4. **Schermata:** legge le viste in sola lettura. Se cambia strumento, i calcoli restano.
**Test:** i totali ufficiali dei corrispettivi 2025 di `ANALISI IVA` sono il caso di prova: le viste devono dare gli stessi numeri.

## 6. Accantonamento con dati incompleti
Il commercialista manda i riepiloghi in ritardo e Matteo ha ogni mese **solo l'incasso lordo dei due negozi**, preso a mano. L'accantonamento è quindi una **previsione che si corregge**:
1. **Rapporto di partenza dall'anno scorso:** dai dati veri del 2025 (IVA effettivamente versata e corrispettivi lordi) si calcola quanta IVA si è pagata ogni 100 € di incasso, anche per mese o trimestre (stagionalità). Il numero include già gli acquisti detratti, che oggi non si vedono.
2. **Ogni mese:** accantonamento provvisorio = incasso lordo del mese × rapporto (più un margine prudenziale da concordare). L'app dice «metti via X € per il versamento del <data>» e lo confronta con quanto è già accantonato.
3. **Quando arriva il riepilogo del commercialista:** si inserisce l'importo reale, la stima viene sostituita, si vede la differenza (accantonato contro dovuto) e il rapporto si aggiorna con la media mobile degli ultimi mesi veri.
**Come entrano i corrispettivi mensili:** bastano due numeri (negozio 17 e negozio 21). Partenza: **modulo n8n a mano con i due totali, con la foto del documento allegata** all'archivio. Lettura automatica dalla foto: più avanti, con OCR locale (meno preciso sulle stampe) o con un servizio esterno a pagamento che vede la foto; in ogni caso con conferma dei valori e controllo della somma. Promemoria mensile a Matteo.
**Limite:** è una stima, non il calcolo dell'IVA. Finché gli acquisti non entrano, l'errore dipende da quanto cambiano da un anno all'altro. L'app mostra sempre «stima» e «reale» separati. Percentuali e regole vanno concordate con il commercialista e scritte in un solo posto, con data e fonte.

## 7. Fasi
- **Fase 1:** Postgres e backup; flusso fattura estera con invio al commercialista; import CSV e dashboard base; scadenzario con accantonamento e avvisi; riepilogo per Mirca.
- **Fase 2:** registro comunicazioni IVA; archivio documentale (Paperless-ngx); incassi e corrispettivi giornalieri per sede (17 e 21) con quadratura su estratto conto e IVA stimata; pacchetto mensile per il commercialista.
- **Fase 3:** fatture passive nazionali, prima nota, riconciliazione, buoni (collegamento al modulo buoni di `docs/prd-back-office.md`), altri invii automatici.
- **Riuso:** parser in `ANALISI IVA` (corrispettivi PDF) e in `finanze Matte 2026` (movimenti CSV), da riadattare **senza copiare dati reali nel repository**.

## 8. Da verificare prima di costruire
| Cosa | Chi |
| --- | --- |
| Sistema, RAM e disco della VPS; se ci sono già Postgres e Docker; come si comanda n8n; backup attuali; come è configurato Tailscale e chi entra. Prima in sola lettura, con l'ok di Matteo | Matteo e AI |
| Termine esatto («entro tot giorni») per le fatture estere; indirizzo e formato di invio; regime IVA (mensile o trimestrale); elenco scadenze; cosa serve rispondere per le comunicazioni IVA; formato del pacchetto mensile | Matteo, dal commercialista |
| Quali conti, formato CSV esportabile, ogni quanto si scaricano i report | Matteo |
| SMTP per l'invio (casella Aruba dopo la creazione, o altro) | Matteo |
| Metabase e Paperless-ngx girano comodi sulla VPS; il modulo n8n funziona dal telefono via Tailscale. **Prova con dati finti prima dei dati veri** | AI con Matteo |
| Regola di accantonamento: percentuale, margine e conto di destinazione | Matteo con il commercialista |
| Prova di ripristino del backup | AI con Matteo |

## 9. Sicurezza e privacy
- Dati dell'azienda e dei titolari, non di clienti; restano comunque dati bancari e fiscali riservati.
- Niente PDF di estratti conto copiati in chat o in repository; nel repository solo codice e dati finti.
- Chi entra: solo Matteo, dai dispositivi autorizzati su Tailscale. Postgres con utente di sola lettura per la dashboard e utente di scrittura solo per n8n.
- Se un servizio esterno vede le foto dei documenti (OCR a pagamento), va dichiarato e deciso da Matteo caso per caso.
- Fornitori e trattamento vanno rivisti dal consulente insieme a privacy e condizioni (voce 6 e 11 di `docs/interventi-richiesti-matteo.md`).

## 10. Esito del controllo della VPS (24/11/2026, sola lettura, lanciato da Matteo)
Macchina `hermes-matteo-assistant` (Tailscale 100.124.146.32). Script: `back-office/vps/controllo-sola-lettura.sh`. Non è stato modificato nulla.

**Risorse e cosa gira**
- Ubuntu 24.04.4, 4 CPU, **7,8 GiB di RAM (circa 3,5 liberi)**, disco 145 GB con 87 GB liberi, acceso da oltre 5 settimane.
- **n8n 2.48.6** in Docker (`n8n-lab`), in ascolto **solo su 127.0.0.1:5678**, in salute.
- Un altro progetto, **niche-finder**, con un proprio Postgres (pgvector, 127.0.0.1:5436) e un'interfaccia sulla 8086. C'è anche un **altro Postgres** direttamente sul sistema (127.0.0.1:54329), di cui non so a cosa serva. **Non vanno usati per i dati fiscali.**
- Sulla stessa macchina girano **Hermes** (127.0.0.1:9119, 8642, 33123), vari servizi Node e Python e Tailscale (che serve le porte 443 e 8443 sulla rete privata). **Metabase non c'è**.

**Rete e sicurezza: problemi da risolvere prima di mettere dati fiscali**
1. **Il firewall è inattivo** e non c'è fail2ban.
2. **SSH è aperto a internet** (0.0.0.0:22) con **`PermitRootLogin yes`** e **si entra con la password** di root (Matteo l'ha digitata per lanciare lo script). È il punto più debole: chi indovina o ruba quella password prende tutta la macchina, compresi n8n, Hermes e i dati.
3. Tutti gli altri servizi ascoltano solo in locale o sull'indirizzo Tailscale: bene.

**Valutazione**
- **Risorse:** bastano per la Fase 1 (n8n già presente, un nuovo Postgres, Metabase che da solo usa circa 1 GB); Paperless-ngx in Fase 2 va ricontrollato con la memoria rimasta.
- **Isolamento:** il database fiscale deve essere un **contenitore nuovo e separato** (rete Docker propria, in ascolto solo su 127.0.0.1, utente e password nuovi), non quelli di niche-finder né il Postgres di sistema.
- **Hermes sulla stessa macchina:** è un agente con accesso alla macchina. Va verificato **a quali file e porte può arrivare** prima di mettere lì dati bancari; se può leggere tutto come `root`, i dati fiscali non sono isolati da lui. In quel caso: cartella e database leggibili solo da un utente dedicato, oppure una macchina separata per i dati fiscali.
- **Mettere in sicurezza SSH** (chiavi al posto della password, niente accesso diretto di root, firewall che lascia entrare solo Tailscale, fail2ban) è un **passo obbligatorio prima di qualsiasi dato reale** (voce 35 di `docs/interventi-richiesti-matteo.md`). Va fatto con attenzione per non chiudere fuori Matteo: chiavi provate prima di spegnere la password, una seconda sessione aperta durante la modifica.
