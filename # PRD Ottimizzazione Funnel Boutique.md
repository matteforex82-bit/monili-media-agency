# PRD: Ottimizzazione Funnel "Boutique Digitale & Personal Styling"

> **Aggiornamento del 3 novembre 2026:** questa è la bozza precedente. Il riferimento aggiornato per journey, CTA, recapiti, consulenza, pagamenti, riserve, consegne, cambi e buoni regalo è il **PRD — Journey cliente** in [brainstorming marketing strategie.md](brainstorming%20marketing%20strategie.md). In caso di conflitto valgono le decisioni del nuovo PRD; questa bozza non certifica implementazioni già eseguite. In particolare, i requisiti sullo Staff Helper vanno rivalutati rispetto al vincolo di non conservare dati cliente nello Studio AI.

* **Progetto:** Vetrina Digitale Monili (`monili-vetrina.vercel.app`)


* **Target:** Coding Agent (Cursor, Claude Code, Copilot, Aider)
* **Obiettivo:** Ottimizzare l'architettura frontend del sito per riflettere il posizionamento reale dell'attività: vendita consulenziale, tirature minime/pezzi unici senza magazzino di massa e transizione fluida verso la chat WhatsApp con le stylist del negozio fisico.

---

## 1. Audit e Gap Analysis (Cosa Mantenere vs Cosa Virare)

Il coding agent deve confrontare il codebase corrente con la matrice seguente:

| Ambito | Configurazione Attuale (Da Mantenere) | Direzione da Virare (Nuova Implementazione) |
| --- | --- | --- |
| **Piattaforma di Checkout** | Zero carrello integrato; chiusura esterna via WhatsApp/SumUp.

 | **Nessun carrello self-service.** Conservare la chiusura in chat per prevenire overbooking di pezzi unici. |
| **Tracciamento & Cookie** | Architettura cookieless, zero cookie banner.

 | **Nessun pixel Meta o GA4.** Mantenere il sito privo di banner intrusivi. Usare solo analytics server-side/cookieless se necessari. |
| **Call to Action (CTA)** | CTA generiche o bottoni di contatto standard.

 | **CTA consulenziali ad alto intento.** Modificare bottoni in "Verifica disponibilità & Chiedi consiglio di stile". |
| **Generazione Link WhatsApp** | Messaggio generico o statico.

 | **Deep-linking dinamico per prodotto.** Generare messaggi precompilati con ID, titolo e richiesta di vestibilità. |
| **Percezione del Catalogo** | Semplice elenco foto/schede. | **Scarsità naturale e valore artigianale.** Introdurre badge "Pezzo Unico / Edizione Limitata" su ogni scheda. |
| **Storytelling di Processo** | Assente o implicito. | **Sezione "Come Funziona la Boutique a Distanza"** in home page per educare il cliente prima del clic. |

---

## 2. Nuovi Componenti e Modifiche UI/UX

### Requisito 2.1: Modulo Generazione Link WhatsApp Dinamico

Aggiornare o creare l'utility per la generazione dell'URL WhatsApp in modo da precompilare i parametri del prodotto:

* **File:** `utils/whatsapp.ts` (o analogo nel progetto)
* **Logica:**
```typescript
export interface ProductWhatsappProps {
  id: string;
  title: string;
  category?: string;
}

export function generateProductWhatsappUrl(
  phoneNumber: string,
  product: ProductWhatsappProps
): string {
  const text = `Salve! Ho visto sulla vostra vetrina "${product.title}" (Rif. ${product.id}). ` +
               `È ancora disponibile in boutique? Vorrei chiedervi un consiglio su vestibilità e abbinamenti.`;
  return `https://wa.me/${phoneNumber.replace(/[^0-9]/g, '')}?text=${encodeURIComponent(text)}`;
}

```


* **Attributi link obbligatori:** `target="_blank" rel="noopener noreferrer"`.



---

### Requisito 2.2: Aggiornamento Scheda Prodotto (`components/ProductCard.tsx`)

Modificare la scheda prodotto con i seguenti elementi visivi:

1. **Badge Scarsità:**
* Posizionamento: In alto a sinistra o sopra il titolo del prodotto.
* Testo: *"Pezzo Unico"* oppure *"Disponibilità Limitata in Boutique"*.
* Stile: Discreto, elegante, coerente con il design attuale dei monili.


2. **Pulsante CTA Consulenziale:**
* Sostituire testi tipo "Acquista" o "Ordina" con:
* **Versione estesa:** *"Chiedi consiglio & disponibilità"*
* **Versione compatta (mobile):** *"Consulenza & Disponibilità"*


* Icona: Icona WhatsApp minimale accanto al testo.


3. **Avvertenza di Disponibilità:**
* Inserire una micro-didascalia sotto il bottone:
* *"I nostri capi e gioielli sono presenti anche in boutique: la disponibilità effettiva viene confermata in tempo reale dal nostro team."*





---

### Requisito 2.3: Sezione "Come Funziona la Nostra Boutique" (`components/HowItWorks.tsx`)

Inserire in Home Page (sotto l'hero/intro o prima del catalogo prodotti) un blocco visivo a 3 passaggi per guidare l'utente:

* **Titolo Sezione:** *"L'esperienza della nostra boutique, ovunque ti trovi"*
* **Passo 1:**
* **Titolo:** *Sfoglia la Selezione*
* **Descrizione:** *Capi ricercati, pietre dure e creazioni artigianali selezionate con cura in quantità minime o pezzi unici.*


* **Passo 2:**
* **Titolo:** *Consulenza Dedicata su WhatsApp*
* **Descrizione:** *Le nostre personal stylist sono a tua disposizione dal negozio per darti consigli su misure, abbinamenti e mostrarti il capo dal vivo.*


* **Passo 3:**
* **Titolo:** *Consegna Sicura a Domicilio*
* **Descrizione:** *Conferma il tuo ordine in chat con link di pagamento protetto SumUp o bonifico e ricevi il pacco con corriere espresso tracciato.*



---

## 3. Tool Interno Operativo: Modulo Generatore d'Ordine Rapido

Per snellire il lavoro del personale in cassa ed evitare di scrivere a mano i messaggi di conferma, creare una pagina interna protetta (o visualizzabile solo con parametro query/admin, es. `/staff-order-helper`):

* **Scopo:** Permettere alle commesse di selezionare il prodotto, inserire i dati della cliente e ottenere il messaggio di conferma formale pronto da incollare su WhatsApp.
* **Campi Input del Form:**
* Nome Cliente
* Prodotto / Descrizione
* Prezzo Prodotto (€)
* Spese di Spedizione (default: configurabile da `config/legal.ts` o campo libero)
* Metodo di Pagamento selezionato: Link SumUp / Bonifico Bancario
* Link SumUp generato o coordinate IBAN
* Dati di Spedizione del Cliente (Indirizzo completo, Telefono)


* **Output:**
* Un'area di testo che genera il modello legale su supporto durevole (previsto al punto 6.2 del PRD Legale) con un bottone **"Copia per WhatsApp"** (`navigator.clipboard.writeText`).





---

## 4. Aggiornamento Documento Operativo Negozio (`docs/OPERAZIONI_NEGOZIO.md`)

Il coding agent deve arricchire la guida operativa per il personale con i modelli per le risposte rapide (Quick Replies) di WhatsApp Business:

### Modelli di Risposta Rapida da Integrare:

1. **Richiesta Disponibilità / Misure (`/misure`):**
> *"Ciao! Verifico subito in cassa se il capo è ancora disponibile. Intanto ti confermo che ha una vestibilità regolare. Se vuoi, ti invio un brevissimo video dal vivo per mostrarti la luce della pietra / come cade il tessuto!"*


2. **Video Prova / Dettaglio (`/video`):**
> *"Ecco un breve video girato adesso in boutique dove puoi apprezzare i dettagli reali e la resa dell'indosso. Se desideri abbinarlo con altri gioielli o capi, dimmi pure!"*


3. **Istruzioni Pagamento SumUp (`/sumup`):**
> *"Perfetto, ti abbiamo riservato il capo al banco per le prossime 2 ore. Puoi completare l'acquisto in modo sicuro con qualsiasi carta di credito/debito tramite questo nostro link ufficiale SumUp: [INSERISCI_LINK_SUMUP]. Non appena confermato, prepariamo la confezione regalo e la spedizione!"*



---

## 5. Criteri di Accettazione e Verifica (Definition of Done)

L'agente di sviluppo considera il rilascio completato quando:

1. **Link Dinamici Funzionanti:** Cliccando sul pulsante di ciascuna scheda prodotto, WhatsApp apre una chat verso il numero configurato contenente nome e codice identificativo esatto del capo.
2. **Nessun Regressione su GDPR/AI Act:** Il badge di trasparenza AI (`AiWearBadge.tsx`), i testi legali (`/privacy`, `/cookie`, `/condizioni-vendita`) e l'architettura senza cookie banner rimangono pienamente preservati.


3. **Copy Coerente:** Tutti i pulsanti di acquisto generici sono sostituiti da diciture focalizzate sulla consulenza e la verifica disponibilità.
4. **Sezione "Come Funziona" Visibile:** La nuova sezione a 3 step è integrata nella landing page ed è responsive (ottimizzata per consultazione da smartphone).
5. **Staff Helper Accessibile:** La pagina o componente per la generazione rapida del riepilogo d'ordine per il personale è funzionante e copia correttamente il testo negli appunti.
