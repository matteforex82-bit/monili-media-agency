# Piano editoriale dentro lo Studio: perimetro (bozza del 4/11/2026)

Stato: **versione 1 realizzata in locale il 4/11/2026** (vedi `docs/STATO_PROGETTO.md`). Decisioni di Matteo già prese sono nella sezione 1.

## 1. Decisioni già prese
- Il piano **non lo scrive Matteo a mano**: lo Studio propone cosa creare, secondo le buone pratiche di marketing per I Monili; Matteo **accetta, cambia o salta**.
- Black Friday (27/11/2026): **nessuno sconto né promozione**. Il tema si tratta come le altre idee regalo e nei contenuti non compaiono mai parole come «sconto», «-20%», «promo».
- Resta la cadenza unica: **2 contenuti principali a settimana**, Storie riusate nei 3 giorni successivi, **nessun giorno fisso promesso**.
- Ogni contenuto chiude con «Scrivici, ti diciamo se è disponibile» e, se è di prodotto, ha **prezzo e codice del pezzo** (`M-XXXXX`).
- Valgono tutte le regole già scritte: una donna per pezzo, divieti in `skills/_base/divieti.md`, etichetta «Info sull'AI», mai dati di clienti.

## 2. Cosa vede Matteo (versione 1)
Una pagina **«Piano»** nello Studio:
1. **Questa settimana:** due proposte. Ognuna mostra: tipo di contenuto (skill), pezzo o pezzi consigliati con foto, prezzo, sede e codice; il **perché** in una riga («è la settimana delle idee regalo: 40% delle visualizzazioni dei Reel arriva da chi non ci segue»); il brief già compilato.
2. **Tre bottoni:** «Crea» (apre il Reel Studio con skill, pezzo e brief già pronti), «Un'altra idea» (ne propone un'altra diversa), «Salta questa settimana» (con motivo facoltativo).
3. **Riuso nelle Storie:** per ogni contenuto una promemoria dei 3 giorni successivi (non produzione nuova).
4. **Stato:** da fare, creato, pubblicato, saltato. «Creato» si ricava dai Reel esistenti; «pubblicato» lo segna Matteo.
5. **Prossime settimane:** anteprima delle due settimane dopo, indicata come provvisoria.

## 3. Come lo Studio sceglie i suggerimenti
**Regole fisse (verificabili con test), nell'ordine:**
1. **Calendario eventi** che dà il tema della settimana: idee regalo dal 16/11; settimana del Black Friday (solo idee regalo, senza promozioni); countdown dal 1/12; ponte dell'Immacolata (8/12); ultimi regali (14–20/12); auguri e orari festivi (21–24/12); Capodanno; Befana. Fuori dalle date, tema libero.
2. **Mix per ruolo del contenuto:** ogni settimana uno per **chi non ci conosce** (Reel con hook forte nei primi 3 secondi: indossato, 3 modi, prima/dopo) e uno per **chi vuole comprare** (idea regalo con prezzo, nuovo arrivo, pietra della settimana, mani al bancone). Dati Insights: Storie 62%, Reel 34%, post 3,7%; 40% delle visualizzazioni dei Reel viene da non follower.
3. **Rotazione:** mai la stessa skill due settimane di fila; mai lo stesso pezzo entro 3 settimane; non ripetere donna e scena recenti.
4. **Scelta del pezzo:** solo pezzi pubblicati e disponibili, con prezzo e foto buona; alternanza tra i due negozi (17 argento e pietre, 21 il resto); per i temi di prezzo («sotto i 50 €») solo pezzi nella fascia; i pezzi più recenti hanno priorità.
5. **Conversione:** ogni proposta ha un invito concreto (DM/WhatsApp o passare in negozio). Dato storico: 627 visite al profilo e un solo tocco sull'indirizzo, quindi il negozio va sempre indicato.
6. **Etichette:** se compare una donna AI, la proposta ricorda «Info sull'AI».

**Ruolo dell'AI:** non decide il piano. Dato il tema e i pezzi scelti dalle regole, scrive **brief e motivazione** nel tono del negozio, rispettando divieti, chiusura e prezzo. Senza chiave AI il piano funziona lo stesso con brief standard.

**Versione 2 (non ora):** i suggerimenti tengono conto della pagina Risultati (invii, DM, visite in negozio) e fanno salire le skill che rendono di più.

## 4. Dati e tecnica
- Il piano salvato è un file nello Studio (`memory/piano.json`): settimane, proposte, stato, motivo dei «salta». **Nessun dato di clienti.**
- Nuovo modulo `piano.py` (regole e calendario eventi), nuove rotte in `api/server.py` (`GET /piano`, `POST /piano/{settimana}/{slot}/(altra-idea|salta|pubblicato)`), nuova pagina `frontend/src/app/piano`.
- Il calendario eventi vive in un file dati modificabile (`skills/_base/calendario-eventi.md` o JSON), non nel codice, come le skill.
- `docs/piano-natale-2026.md` resta come riferimento; Black Friday va aggiornato (nessuna promozione).

## 5. Fuori perimetro
Pubblicazione automatica su Instagram, orari di pubblicazione consigliati (dato da verificare), analisi dei concorrenti, caption finali scritte senza il passaggio da Reel Studio, qualsiasi collegamento al registro ordini o a dati clienti.

## 6. Criteri di accettazione (anche condizione per un eventuale `/goal`)
1. La pagina **Piano** mostra la settimana corrente con 2 proposte, ciascuna con skill, pezzo (foto, prezzo, sede, codice), motivo e brief.
2. «Crea» apre il Reel Studio con skill, pezzo e brief precompilati.
3. «Un'altra idea» cambia davvero proposta; «Salta» la registra e non la ripropone la stessa settimana.
4. Test con le regole: nessun pezzo ripetuto entro 3 settimane, nessuna skill uguale a quella della settimana prima, solo pezzi pubblicati con prezzo e foto, nessuna parola promozionale nei brief del Black Friday, chiusura e prezzo sempre presenti.
5. Senza chiave AI la pagina funziona; nessun dato di clienti nel file.
6. `python -m pytest tests` e il build del frontend passano; pagina provata nel browser.

## 7. Ancora da decidere
- Nome della voce nel menu («Piano» o «Idee della settimana»).
- Chi segna «pubblicato»: Matteo a mano nella versione 1 (consigliato) oppure in futuro in automatico.
