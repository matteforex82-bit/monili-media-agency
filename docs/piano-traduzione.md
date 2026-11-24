# Piano: traduzione del sito vetrina

Bozza del 17/11/2026, solo progetto: nessun codice toccato. Nasce dalla frase di Matteo del 17/11 («valutiamo di tradurre tutto il sito, penso sia possibile ma da progettare bene»). Sito: `Ecosistema Monili/apps/web` (Next.js 16.2.4, repo `monili-vetrina`). Non è consulenza legale: dove serve un parere, è scritto come domanda per il consulente.

## In breve

- **Si può fare, e il collo di bottiglia non è il codice ma i testi legali.** Il contratto non si conclude sul sito: si conclude su WhatsApp/Instagram, con riepilogo (modello B) e conferma su supporto durevole (modello C) di `impegni-legali.md`. Anche il ritiro in negozio di un ordine confermato a distanza è un contratto a distanza (sezione «Ritiro in negozio di un ordine a distanza» in `legal-content.ts`). Un sito in inglese che invita a chiedere un pezzo porta quindi a un acquisto in inglese: servono riepilogo e condizioni in inglese, rivisti da un consulente.
- **Raccomandazione: opzione B**, inglese completo, in due tempi: prima tutto tranne le promesse legali (vetrina, schede, negozi, chatbot), poi i testi legali in inglese insieme alla revisione del consulente, che è già in sospeso per l'italiano. Italiano e inglese vanno rivisti **insieme**, in un solo incarico.
- **Tempi**: il sito è «tutto» in inglese solo quando il consulente ha chiuso. Il resto può essere pronto prima. Il lavoro tecnico non serve prima di Natale: la fonte che abbiamo (PRD, riga «Estate») indica i turisti come pubblico d'estate. Proposta: refactoring a gennaio-febbraio, testi a marzo, online per la primavera. Il consulente va contattato **ora**, perché è il percorso più lungo.
- Non si usa nessun widget di traduzione a runtime (Google Translate, DeepL, simili): violerebbe C2/C4 di `impegni-legali.md` e lascerebbe tradurre i testi legali a una macchina senza controllo.

## 1. Lingue e ordine

| Passo | Lingua | Motivo | Stato |
|---|---|---|---|
| 1 | **Inglese** | Unica lingua che il PRD (riga «Estate: turisti, anche crociere») suggerisce; lingua ponte | Raccomandato |
| 2 | Tedesco, francese, spagnolo… | Solo se i dati lo chiedono | **Da decidere con dati**: Matteo guarda in Instagram Insights (paesi del pubblico) e in Google Business (da dove arrivano le ricerche), e dice quali nazionalità vede in negozio. Non abbiamo questi numeri, non li inventiamo |

Il codice si costruisce già per più lingue: aggiungerne una significa una cartella, un dizionario e un glossario. L'inglese è generico (`en`), non `en-US` o `en-GB`.

Impatto sul PRD: oggi dice «lancio dell'assistenza in italiano, non promettere videoconsulenza in altre lingue» (§1, §7). Se si procede, va aggiornato: il PRD va allineato prima del codice.

## 2. Indirizzi, hreflang, sitemap, llms.txt, JSON-LD

**Indirizzi.** Italiano resta alla radice (`/`, `/negozi`, `/p/<id>`: nessun URL esistente cambia, nessuna perdita SEO). Inglese sotto `/en/` (`/en/`, `/en/stores`, `/en/p/<id>`). Sottocartelle e non dominio separato: un solo dominio, un solo hosting, autorità SEO condivisa. Lo slug del pezzo resta quello italiano (`/en/p/<stesso id>`): abbina le due versioni senza tabelle di slug; un po' meno elegante, accettabile.

**Struttura del codice** (verificato sulla documentazione di Next 16 inclusa nel repo, `internationalization.md` e `layout.md`; il repo avvisa: «This is NOT the Next.js you know»):

| Approccio | Pro | Contro |
|---|---|---|
| **Gruppi di route con più layout radice**: `app/(it)/…` (spostamento, URL invariati) e `app/en/…`, ognuno con il suo `<html lang>`; pagine condivise come componenti che ricevono `lang`; `admin/`, `api/`, `sitemap.ts`, `robots.ts` restano fuori dai gruppi | Nessun intermediario sulle richieste, italiano identico, `lang` corretto per pagina | Navigare tra i due gruppi ricarica la pagina (per un cambio lingua va bene). **404 non verificato**: senza layout in cima, le URL che non corrispondono a nessuna route richiedono `global-not-found` (sperimentale) o un layout radice proprio: **da provare prima di decidere** |
| `app/[lang]/…` + `proxy.ts` che riscrive l'italiano su `/it` | È il modello della guida ufficiale, un solo layout | Proxy su ogni richiesta, tutte le pagine vanno spostate sotto `[lang]` e l'italiano passa da una riscrittura: più rischio per il sito già online |

Raccomandazione: i gruppi di route, **dopo una prova di 404 e di build**; se la prova non convince, `[lang]` col proxy. Una prova di regressione: lo HTML dell'italiano prima e dopo lo spostamento deve essere identico.

**Nessuna scelta automatica della lingua.** Niente reindirizzamento da `Accept-Language`, niente cookie di preferenza (`impegni-legali.md` C1): l'indirizzo è la preferenza. Un selettore «IT · EN» visibile nell'header. Se si usasse `next-intl`, serve `localeCookie: false` e rilevamento spento; consiglio un dizionario tipizzato nostro (come già fa il chatbot), senza nuova dipendenza.

**hreflang.** Su ogni pagina disponibile in due lingue: `alternates.languages` (`it`, `en`, `x-default` → italiano) più canonical su se stessa, in entrambi i versi. Una pagina inglese che non esiste (pezzo non tradotto) non genera hreflang né voce in sitemap. Le pagine nascoste restano solo italiane e `noindex`.

**Sitemap.** Una sola sitemap, ogni voce con `alternates.languages` (supportato da `MetadataRoute.Sitemap`). Le pagine legali inglesi entrano solo quando sono pubblicate (§5).

**llms.txt.** `/llms.txt` resta in italiano; nuovo `/en/llms.txt` in inglese con negozi, orari, «Arrivals» (solo pezzi con testo inglese approvato). `robots.ts` invariato.

**JSON-LD.** Stesse entità (`@id` condivisi per i due negozi), `inLanguage`, nome e descrizione nella lingua della pagina; `Product` inglese solo dove c'è il testo inglese; `openGraph.locale` `en_GB` o `en` (da scegliere, non cambia nulla di sostanza). L'escape di `jsonLd()` resta.

**Da localizzare nel codice** (non solo i testi delle pagine): `formatPrice` (`22,50 €` → `€22.50`), `categoryLabel`, `stateLabel`, `openingHoursLabel` e `openNowLabel` (giorni e frasi italiane in `shop-hours.ts`: dati separati dalla frase), `buildWhatsappMessage`, `GIFT_BANDS`, `<html lang>`, link «Vai al contenuto», `aria-label`, footer. L'area `/admin` e le sue API restano in italiano.

## 3. Testi dei pezzi dallo Studio, foto con etichetta IA

**Stato verificato**: la scheda è salvata come JSONB (`product_fiches.payload`) e `parseNewProduct` ricostruisce l'oggetto campo per campo. Conseguenze:
- **Nessuna migrazione del database** per aggiungere campi inglesi.
- **Ordine di rilascio obbligato**: prima il sito accetta e valida i campi inglesi, poi lo Studio li invia. Se lo Studio parte prima, il sito li scarta in silenzio e il lavoro va perso (nessun errore).

**Opzioni per i testi** (titolo, `summary`, `story`, materiali, `alt` delle foto, `seo`):

| Opzione | Costo | Rischio | Giudizio |
|---|---|---|---|
| a) A mano | Alto, ogni pezzo | Lento: i pezzi nuovi arrivano senza testo inglese | No come regola, sì come correzione |
| **b) Lo Studio li scrive all'ingresso** (nella stessa fase che oggi fa i testi italiani, con una skill `skills/` e un glossario: ametista = amethyst, smaltato = enamelled, pezzo unico = one of a kind…) e **Matteo li approva** nell'admin accanto all'italiano | Basso, qualche centesimo | Errori sui fatti (materiali, misure, prezzo); mitigato da controlli automatici: stessi numeri nei due testi, stessi materiali, nessuna promessa vietata («hold it for you») | **Raccomandata** |
| c) Traduzione automatica a ogni visita | Zero | Testo non controllato sul sito, dipende da un servizio di terzi | No (C2/C4) |

Dettagli di b): testo scritto come adattamento, non parola per parola, e nel tono «amica» del brand. Nomi propri dei pezzi invariati (es. «Anello Cavour»), ma con la parola comune tradotta. Numeri, prezzi e taglie non si convertono: taglia italiana indicata come tale. Dati dei clienti mai nel prompt (P8): i testi dei pezzi non ne contengono. Campo `translations.en` con `reviewedAt`: l'italiano si pubblica subito come oggi; la versione inglese compare solo se approvata. La home inglese mostra solo i pezzi con testo approvato. I 2 pezzi online di oggi si traducono una volta sola con uno script; con 8-10 pezzi (obiettivo del 15/11) la revisione è un controllo breve.

**Foto con etichetta IA.** Il flag `aiGenerated` non dipende dalla lingua: segue la foto. Cambiano il testo del badge `AiWearBadge` e l'`alt`. L'etichetta va tradotta **dal primo giorno** su ogni pagina inglese che mostra foto IA: è un'informazione al visitatore, non una clausola. Se debba essere nella lingua della pagina secondo l'AI Act è una domanda per il consulente (§5), ma la scelta prudente e a costo zero è tradurla comunque. Sulla frase della clausola «fanno fede le caratteristiche del pezzo reale»: segue il trattamento dei testi legali.

## 4. Prezzi, spedizioni all'estero, consulenza

- **Prezzi**: solo in euro, «VAT included» (imposte incluse, V6). Nessun convertitore di valuta (servirebbe una fonte esterna di cambi e il prezzo mostrato non sarebbe quello pagato).
- **Spedizioni**: la decisione del 17/11 (fuori Italia sì, costo più alto, paesi e prezzi da definire) esiste solo come frase neutra. Sul sito inglese, finché non ci sono paesi e prezzi: «We ship within Italy (€8, free over €99). For other countries, write to us: we confirm the cost before you pay». Non si pubblicano paesi, cifre o tempi. Domande fiscali e di diritto del consumatore estero: al consulente (§5).
- **Consulenza**: oggi solo in italiano, e il PRD vieta di promettere altre lingue. Sul sito inglese **non esiste**: pagina, voce di menu, sitemap e percorso del chatbot spariscono (il bot già legge `consultationEnabled`: si aggiunge `consultationLanguages`). Si riapre solo se Barbara e Mirca vogliono farla in inglese.
- **Risposte ai messaggi**: chi risponde in WhatsApp/Instagram alle richieste in inglese? È una decisione organizzativa, non tecnica: il sito non deve promettere un servizio che non c'è.

## 5. Testi legali (`legal-content.ts`: privacy, cookie, condizioni di vendita)

**Regola proposta**: nessuna traduzione non rivista da un consulente si pubblica come testo vincolante. Italiano resta unico testo di riferimento fino a revisione conclusa.

| Fase | Cosa si pubblica in inglese | Condizione |
|---|---|---|
| Prima della revisione | Nessuna pagina legale inglese come tale. Il footer inglese rimanda ai testi italiani, con una riga: «Our legal texts are in Italian. For an English version before any purchase, write to us» | La riga è una **promessa**: si può onorare solo se esiste una versione inglese pronta. Se non c'è, la riga si toglie e le richieste in inglese restano «chiedi disponibilità, si compra dopo la revisione». Decisione di Matteo e del consulente |
| Dopo la revisione | `/en/privacy`, `/en/cookie`, `/en/terms`, `/en/llms.txt` aggiornato, modelli B-E in inglese, stesso testo nei messaggi | Campo `reviewedAt` per lingua; la pagina inglese è raggiungibile e in sitemap solo se `reviewedAt` c'è. Test: tutte le cifre (8 €, 99 €, 14 giorni, 2-3 giorni, 48 ore) e le frasi vietate («te lo mettiamo da parte» e la sua versione inglese) verificate in inglese come in italiano, estendendo `legal-compliance.test.ts` |

**Perché prima la revisione del consulente**: la privacy e le condizioni non sono ancora riviste nemmeno in italiano. Tradurle ora significa raddoppiare il lavoro da correggere. Un solo incarico, due lingue.

**Domande per il consulente** (nessuna risposta è assunta in questo piano):
1. Una versione inglese non vincolante, con l'italiano come testo che prevale, è accettabile verso i consumatori? Oppure serve un testo vincolante in inglese per chi compra con un sito e una chat in inglese?
2. Quali regole del consumatore residente all'estero si applicano se il sito è in inglese e spediamo fuori dall'Italia? E fuori dalla UE (Regno Unito, Stati Uniti)?
3. IVA sulle vendite a distanza verso altri paesi UE e verso extra-UE; dogane; tax-free per turisti extra-UE: se applicabile ai pezzi e a noi.
4. L'informativa privacy e l'etichetta «immagine IA» devono essere nella lingua della pagina?
5. Un ordine confermato in inglese su WhatsApp e ritirato in negozio resta contratto a distanza (come dicono le condizioni): servono riepilogo e conferma in inglese su supporto durevole?

## 6. SEO, velocità, nessun cookie né terzi

| Tema | Impatto | Nota |
|---|---|---|
| **SEO** | Positivo se fatto bene: pagine nuove senza toccare le italiane; hreflang bidirezionale; pezzi senza testo inglese non appaiono (niente contenuto duplicato o in lingua sbagliata) | Rischio: testi inglesi copiati dall'italiano o tradotti male. Fuori dal sito: descrizione inglese nel profilo Google Business, menzione nella bio Instagram. Misura: **Search Console** (si verifica con un record DNS o un file, nessun codice sul sito) per paese e ricerca; niente Analytics (C1) |
| **Velocità** | Italiano invariato. Pagine inglesi statiche come le altre (rigenerate ogni ora per i pezzi). Il dizionario resta sul server; nel browser va solo ciò che serve al chatbot, caricato in lazy | Font: il sottoinsieme latino basta per l'inglese. Per polacco o lingue con caratteri estesi servirebbe `latin-ext` (peso in più). Da rimisurare con Lighthouse (oggi 100/100/100 su accessibilità, best practices e SEO, performance 85-88 in locale) |
| **Cookie e terzi** | Nessuno: lingua nell'indirizzo, niente preferenze salvate, nessun SDK | Resta valido C1-C4. Un widget di traduzione, un servizio di localizzazione a runtime o un CDN di traduzioni violano C2/C4 |
| **Sicurezza** | CSP e intestazioni in `next.config.ts` valgono anche per `/en` | |
| **Manutenzione** | Ogni testo nuovo del sito va scritto in due lingue: tipi TypeScript con le stesse chiavi per tutte le lingue, così una chiave mancante fa fallire la build | Matteo deve accettare che aggiornare il sito costi il doppio dei testi |

## 7. Chatbot (`chatbot-engine.ts`, `TESTI_CHATBOT.md`), sempre senza AI

Il motore è una funzione pura da stato a messaggio: si presta. I testi italiani oggi sono dentro il motore (579 righe). Passi:
1. **Estrarre i testi** in un dizionario per lingua (`chatbot-content.ts` come previsto dalla specifica §12); stessi id di nodo, stesse opzioni.
2. **Percorsi**: gli stessi, tranne la consulenza (§4). Dati dinamici (pezzi, orari, numero) dai moduli del sito, localizzati.
3. **Testo libero locale**: parole chiave e tolleranza ai refusi **per lingua** (nessuna AI, nessuna richiesta di rete): è la parte nuova da scrivere e provare con frasi inglesi vere.
4. **API `api/chatbot/regali`**: riceve la lingua, restituisce titoli e testi inglesi, solo dei pezzi con testo approvato.
5. **Messaggio WhatsApp precompilato**: scritto in inglese, comprensibile a chi risponde. Chi risponde capisce e risponde in inglese? (domanda a Matteo.)
6. **Test**: parità tra lingue (stessi nodi, stessi vicoli ciechi esclusi), cifre uguali a `legal-content.ts`, frasi vietate in entrambe le lingue, nessun numero diverso dal centrale, `helpNeeded` identico, nessuna richiesta di rete in uscita.
7. La lingua del chatbot segue la pagina: in `/en` parla inglese, in italiano resta com'è.

Prima della revisione del consulente (§5), le risposte del bot su spedizioni, resi e pagamenti in inglese riassumono soltanto le cifre già pubblicate e rimandano alle pagine; dopo la revisione si allineano al testo approvato.

## 8. Tre opzioni a confronto

| | **A. Vetrina inglese minima** | **B. Inglese completo, in due tempi** (raccomandata) | **C. Più lingue subito** |
|---|---|---|---|
| Cosa | `/en/` con poche pagine: home, negozi, come arrivare, 5-10 pezzi; legale solo in italiano; chatbot in italiano | Tutto il sito e il chatbot in inglese; legale inglese dopo la revisione; dizionari pronti per altre lingue | Inglese + tedesco + francese (+ spagnolo) in una volta, con traduzione automatica da rivedere |
| Lavoro (**stime**, da verificare) | circa 2-3 giorni | circa 6-8 giorni di sviluppo, più la revisione dei testi di Matteo | oltre 12 giorni e una revisione per lingua |
| Rischio legale | Basso solo se non si invita a comprare a distanza; è il rischio che nasce dall'invito | Contenuto: i testi legali aspettano il consulente | Alto: più lingue da far rivedere, regole di più paesi |
| SEO | Poco contenuto, ma pulito | Buona copertura inglese, hreflang completo | Più mercati, ma senza dati su quali servono |
| Manutenzione | Bassa | Raddoppia i testi nuovi | Moltiplica per lingue; i pezzi nuovi vanno in 4 lingue |
| «Tutto il sito» | No | **Sì**, ma i testi legali inglesi solo dopo il consulente | Sì in apparenza, rischioso |
| Se i pezzi online restano 2 | Va bene: pochi pezzi da tradurre | Va bene, ma la home inglese è scarna finché non si arriva a 8-10 pezzi | Spreco |

A ha il merito di essere reversibile e veloce; ci si può fermare lì se Matteo non vuole ancora impegnarsi. È meno adatto se l'obiettivo è che chi legge in inglese possa anche fare un acquisto.

## 9. Raccomandazione e ordine di lavoro

**Opzione B.** Ordine:
0. Risposte di Matteo (sotto) e **incarico al consulente** per italiano + inglese (parte subito, è il percorso più lungo).
1. PRD e `impegni-legali.md`: aggiornare (§10).
2. Prova tecnica: 404 con più layout radice, build, regressione dell'italiano identico.
3. Struttura multilingua, dizionari tipizzati, selettore lingua, localizzazione di prezzi, orari, etichette. Italiano invariato.
4. Pagine statiche inglesi (home, negozi, chi siamo, idee regalo), metadata, hreflang, sitemap, `llms.txt`, JSON-LD.
5. Schede dei pezzi: campi inglesi nel sito (validazione, store, admin con approvazione), **poi** lo Studio.
6. Chatbot in inglese e test di parità.
7. Controlli: Lighthouse, accessibilità, validazione hreflang, nessuna richiesta esterna, test del repo.
8. Testi legali e modelli B-E in inglese, a revisione conclusa; poi si apre l'invito all'acquisto in inglese.

## 10. Documenti da aggiornare se si procede

- **PRD (`brainstorming marketing strategie.md`)**: oggi italiano soltanto; aggiungere la decisione sull'inglese e il divieto di consulenza in altre lingue, finché vale.
- **`impegni-legali.md`**: nuove promesse (la riga «versione inglese su richiesta», se la si tiene; lo stesso numero di spedizione in inglese; nessun widget di traduzione, sotto C2/C4), modelli B-E in inglese.
- **`SPECIFICA_CHATBOT.md`**: §14 e §16 («Inglese rimandato al progetto di traduzione») si chiudono con questo piano; la regola `consultationEnabled` si estende per lingua.
- **`CLAUDE.md` del progetto**: regola per chi sviluppa: ogni testo nuovo in tutte le lingue attive, mai un widget di traduzione.

## 11. Domande per Matteo

In ordine di importanza, ognuna con la mia raccomandazione:

1. **Procediamo con l'opzione B e il consulente su italiano + inglese insieme?** Sì; è l'unica via che porta a «tutto il sito» senza testi legali non rivisti. Se vuoi spendere meno ora, l'opzione A senza invito all'acquisto.
2. **Chi risponde ai messaggi in inglese su WhatsApp e Instagram, e chi ha un inglese sufficiente per approvare i testi dei pezzi?** Senza una persona il sito non deve promettere risposte in inglese; l'approvazione dei testi è un controllo sui fatti (materiali, misure, prezzo), non letterario.
3. **Quali nazionalità vedi davvero in negozio e nelle statistiche?** Serve a decidere se dopo l'inglese ha senso un'altra lingua. Raccomandazione: non decidere prima di aver guardato Instagram Insights e Google Business.
4. **Spedizioni fuori dall'Italia: in inglese diciamo «scrivici, ti diciamo il costo prima di pagare» finché non definisci paesi e prezzi?** Sì.
5. **Consulenza gratuita solo in italiano, quindi assente sul sito inglese?** Sì, salvo che tu e Mirca la vogliate fare in inglese.
6. **Quando partire?** Consiglio: contatto col consulente subito, lavoro sul codice a gennaio-febbraio, online in primavera, per non toccare il sito durante il periodo di Natale. Se per te il turismo conta prima, si anticipa l'opzione A.
7. **Pezzi online: tradurre solo quelli nuovi dal momento del rilascio, o anche i primi 2?** Anche i primi 2 (script una tantum).

## Fonti lette

`docs/impegni-legali.md`, `PLAN_VETRINA.md`, `Chatbot Sito/SPECIFICA_CHATBOT.md` (repo `monili-deploy-temp`); `apps/web` di `monili-vetrina`: `AGENTS.md`, `next.config.ts`, `src/app/layout.tsx`, `sitemap.ts`, `robots.ts`, `llms.txt/route.ts`, `src/lib/legal-content.ts`, `site-config.ts`, `product-fiche*.ts`, `json-ld.ts`, `chatbot-engine.ts`, `consulenza/page.tsx`, e la documentazione di Next 16 in `node_modules/next/dist/docs`. Non verificati: cosa fa realmente `global-not-found` in questa versione; cosa dicono le pagine di dettaglio dell'admin sul modo di mostrare un secondo testo; le abitudini del pubblico (nessun dato nelle fonti lette).

---

## 12. Come separare il sito inglese da quello italiano (progetto)

Obiettivo (richiesta di Matteo, 17/11/2026): l'inglese non deve poter rompere l'italiano, si deve poter accendere, spegnere e tornare indietro da solo, e l'italiano di oggi resta identico fino all'ultimo byte.

### 12.1 Quanto separare: tre livelli

| Livello | Cosa | Pro | Contro | Giudizio |
|---|---|---|---|---|
| **S1. Stessa app, stesso deploy, cartelle e dizionari separati** | `app/(it)/…` e `app/en/…`, testi in `i18n/it` e `i18n/en`, dati condivisi | Un solo catalogo, un solo admin, un solo database, hreflang e sitemap semplici, nessun costo in più | La separazione è di disciplina e di test, non fisica | **Raccomandato**, con le protezioni di §12.3 |
| S2. Stesso repo, secondo progetto Vercel su `en.imoniliravenna.it` | Due deploy dallo stesso codice | Deploy e rollback indipendenti | Secondo progetto (il piano Hobby non ammette siti commerciali, quindi un secondo Pro), variabili e Blob duplicati, autorità SEO divisa tra dominio e sottodominio | No |
| S3. Repo e sito separati per l'inglese | Un sito inglese a sé | Isolamento totale | Il catalogo va sincronizzato due volte (Studio, admin, venduto), doppia manutenzione di tutto | No |

### 12.2 Mappa delle cartelle (S1)

```
src/app/
  (it)/    layout.tsx (html lang=it, header/footer/chatbot di oggi)
           page.tsx, negozi/, chi-siamo/, idee-regalo/, consulenza/, p/[slug]/,
           privacy/, cookie/, condizioni-vendita/, collezioni/ ... (spostati, URL invariati)
  en/      layout.tsx (html lang=en)
           page.tsx, stores/, about/, gift-ideas/, p/[slug]/     (legale e consulenza: §4 e §5)
  (admin)/ layout.tsx (html, body, noindex), admin/ e login
  api/, sitemap.ts, robots.ts, llms.txt/route.ts, en/llms.txt/route.ts   (fuori dai gruppi)
src/i18n/
  routes.ts    una sola tabella: pagina -> indirizzo it / en (alimenta hreflang, selettore, sitemap)
  it/  en/     dizionari tipizzati, stesse chiavi; contenuti lunghi (chi siamo) in file propri
src/lib/       dati e logica condivisi, senza testi di interfaccia
src/components/  componenti condivisi che ricevono `lang` e i testi, non li contengono
```

Verificato in lettura: oggi `app/layout.tsx` è l'unico layout radice, `admin/layout.tsx` non ha `html/body`, non esiste `not-found.tsx`, i test sono `vitest` su `src/**/*.test.ts` e non c'è CI oltre a dependabot. Quindi: l'admin va spostato in un gruppo con un suo layout radice (da controllare che header e footer di oggi non gli servano), e il 404 si decide nella prova tecnica del passo 1.

Indirizzi inglesi tradotti (`/en/stores`, non `/en/negozi`), con lo slug del pezzo invariato. Ogni coppia di pagine sta in `routes.ts`: se manca una voce, il test fallisce.

### 12.3 Regole che tengono i due siti separati

1. **Direzione unica delle dipendenze**: i file di `(it)` e `i18n/it` non importano da `en` o `i18n/en`, e viceversa; regola `no-restricted-imports` di ESLint per cartella.
2. **Nessun testo di interfaccia dentro `lib/` o dentro i componenti**: arrivano dal dizionario della lingua. Chiavi identiche nei due dizionari: una mancante fa fallire la build.
3. **Regressione dell'italiano**: prima di spostare file si salva l'HTML di home, negozi, chi siamo, idee regalo, una scheda, privacy, cookie, condizioni, sitemap e `llms.txt`. Dopo ogni passo, stessi byte, tranne `lang`, hreflang e selettore aggiunti di proposito e ben visibili nella differenza.
4. **Interruttore** `EN_SITE` = `off | preview | on`:
   - `off`: `/en` risponde 404, nessun selettore, nessun hreflang, nessuna voce in sitemap. Il sito è identico a oggi.
   - `preview`: `/en` raggiungibile con `noindex` e fuori dalla sitemap; solo per le prove (anche su Vercel Preview).
   - `on`: tutto attivo.
   Si accende con una variabile, senza toccare il codice, nello stile di `assertProductionEnv`; rollback = rimetterla a `off` e rifare il deploy.
5. **Cancelli per contenuto**, indipendenti dall'interruttore: un pezzo appare in inglese solo con `translations.en.reviewedAt`; una pagina legale inglese solo con `reviewedAt`; la consulenza non esiste in inglese.
6. **Lo spostamento dei file italiani è un commit a sé**, senza altre modifiche, su un ramo dedicato (`feature/en`). Nessun push su `master` senza l'ok di Matteo (PLAN_VETRINA §10).
7. **Dati**: stesso database e stesso Blob; l'inglese è un campo in più nel JSONB. L'admin resta in italiano e unico.
8. **Misura dopo l'accensione**: Search Console, niente Analytics.

### 12.4 Passi piccoli, ognuno verificabile da solo

| # | Passo | Verifica |
|---|---|---|
| 1 | Prova tecnica di 404 e admin con più layout radice, su un ramo usa-e-getta | Build; `/`, `/admin`, un URL inesistente e `/api/*` rispondono come oggi |
| 2 | Spostamento di sole cartelle in `(it)` e `(admin)` | Regressione del punto 3: nessuna differenza |
| 3 | `routes.ts`, dizionario italiano estratto dai componenti (senza cambiare un carattere), tipi per le chiavi | Regressione, `tsc`, lint, test |
| 4 | Interruttore `EN_SITE` e layout inglese vuoto | `off` = 404; `preview` = pagina vuota `noindex` |
| 5 | Dizionario inglese e pagine statiche | Chiavi complete, hreflang bidirezionali, Lighthouse |
| 6 | Schede dei pezzi (prima il sito, poi lo Studio) | Test di contratto con una scheda con testi inglesi |
| 7 | Chatbot | Test di parità del §7 |
| 8 | Accensione `on` | Controllo a mano su telefono e desktop |

---

## 13. Si può far fare questo lavoro ad Haiku?

**Risposta breve**: non tutto, e non da solo. Haiku (il modello più piccolo, quindi più economico e veloce) va bene per pezzi **stretti, meccanici e verificabili da un test**. Non va lasciato a decidere architettura, testi legali o parti dove un errore non si vede. Con i controlli del §12.3 il rischio sui pezzi adatti è basso; senza, no.

| Lavoro | Haiku? | Perché |
|---|---|---|
| Prova tecnica di 404 e admin con più layout radice (passo 1) | No | Documentazione sperimentale di Next 16 da interpretare; un errore compromette tutta la struttura |
| Spostare cartelle in `(it)`/`(admin)` (passo 2) | Sì, con la regressione | Meccanico; il confronto dei byte dell'italiano è il giudice, non il modello |
| Estrarre i testi italiani nel dizionario (passo 3) | Sì, a porzioni, con la regressione | Copia fedele; il rischio è cambiare una parola senza accorgersene, e il confronto lo scopre |
| `routes.ts`, interruttore, hreflang, sitemap, JSON-LD | No | Poche righe con conseguenze su SEO e indicizzazione: vanno pensate e riviste da un modello più forte |
| Bozza dei testi inglesi brevi (menu, etichette, bottoni, FAQ) | Sì, come bozza | Rapido; poi controllo di Matteo e, se possibile, di un madrelingua |
| Testi lunghi di brand (chi siamo, home) e tono «da amica» | Con cautela | Il limite probabile è la naturalezza: meglio un modello più forte o una revisione più attenta |
| Testi legali, modelli B-E in inglese | **No come testo finale** | Decide il consulente (§5). Un modello può dare una bozza di lavoro, nulla di più |
| Traduzione dei pezzi all'ingresso (Studio) | Sì, con controlli | Testi brevi e ripetitivi: con glossario e controlli automatici (stessi numeri e materiali). Da provare su 10-20 pezzi confrontando con un modello più forte prima di fidarsi |
| Chatbot: parole chiave inglesi | Parziale | Le parole chiave sì; motore e test di parità no: sono il punto delicato |
| Validazione dell'ingest, API, sicurezza | No | Cambia una superficie esposta (token, input): revisione con un modello forte e `security-review` |
| Revisione finale e `code-review` | No | Chi scrive non deve giudicare da solo |

**Come farlo in modo efficace e sicuro, se si usa Haiku**
1. **Autore e revisore diversi**: un modello forte progetta e scrive il brief; Haiku esegue un passo alla volta; un modello forte rivede ogni differenza prima dell'unione.
2. **Brief strettissimi**: quali file può toccare, quali no, quale test deve passare, e «fermati e chiedi» se serve altro.
3. **Ramo e cartella isolati** (worktree): non lavora su `master` né sulla cartella di Matteo e non fa push, deploy o cancellazioni.
4. **I test sono il guardrail**: regressione dell'italiano, parità delle chiavi, `tsc`, lint, `vitest`, `build` dopo ogni passo. Se per un passo il test non esiste, quel passo non è per Haiku.
5. **Niente segreti né dati dei clienti** nei brief e nei file (P8 di `impegni-legali.md`).
6. **Misurare prima di estendere**: si fa un passo, si guardano la differenza e le correzioni che ha richiesto, e solo se vanno bene si prosegue.
7. **Il risparmio è reale solo se la revisione costa meno di scrivere**: da verificare sul primo passo.

**Cosa non so**: non ho provato Haiku su questa repo, quindi non posso garantirne la qualità: la valutazione sopra riguarda il tipo di lavoro. I passi 2 e 3 sono il banco di prova giusto: meccanici e con un giudice automatico.

### Decisioni che servono a Matteo per questa parte
1. **Separazione S1** (stessa app, interruttore `EN_SITE`)? Raccomando sì.
2. **Indirizzi inglesi tradotti** (`/en/stores`)? Raccomando sì.
3. **Haiku sui passi 2-3 come prova**, con revisione di un modello forte, e il resto a un modello più forte? Raccomando sì.
