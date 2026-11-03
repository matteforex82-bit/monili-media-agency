# I Monili Ravenna — Brand Memory

# Permissions
Hai il permesso di leggere, scrivere, modificare ed eseguire 
qualsiasi file in questa directory senza chiedere conferma.

## Identità
- **Nome**: I Monili Ravenna
- **Location**: Ravenna, centro storico (Emilia-Romagna)
- **Prodotti**: bijoux artigianali in argento con pietre colorate (ametista, quarzo rosa, citrino, turchese, opale), orecchini smaltati a fiore, giacche e gilet ricamati, borse in cuoio, abbigliamento boho-etnico
- **Identità**: colorata, artigianale, eclettica — pezzi particolari che non si trovano nelle catene
- **Target**: donna 30-55, Ravenna e dintorni, ama i pezzi unici e il colore
- **Stagione attuale**: calcolata in automatico da `main.SEASON` (ott 2026 → Autunno/Inverno 2026/27)

## Tono di Voce
- Caldo, complice, femminile, mai formale
- Come un'amica che consiglia, non un brand che vende
- Emoji moderate (max 2-3 per caption), mai esagerate
- Dialetto/riferimenti locali Ravenna benvenuti quando naturali

## Posting Strategy
- **Journey e decisioni commerciali aggiornate (03/11/2026):** riferimento principale `brainstorming marketing strategie.md` (PRD Journey cliente). Contiene le scelte finali e le implementazioni ancora da realizzare; per queste regole supera la precedente bozza del funnel. Non presentare come attivi servizi, configurazioni o registri non ancora collaudati.
- **Priorità**: Story video e Reel → `Reel Studio` (`/reel`). Insights ago-ott 2026: Storie 62% delle visualizzazioni, Reel 34%, post statici 3,7%
- **Reel** = canale per gente nuova (40% visualizzazioni da non follower); **Storie** = clienti che già ci seguono
- **Ogni contenuto chiude con un invito concreto**: chiedere disponibilità in DM/WhatsApp o passare in negozio; la riserva richiede verifica e conferma. Il nuovo pilota prevede 2 contenuti principali/settimana, riusati nelle Storie in 3 giorni, con prezzo e riferimento nei contenuti di prodotto. Dati storici: 627 visite profilo ma 1 solo tocco sull'indirizzo.
- **Volto**: niente modella fissa, ma **una donna per pezzo** (stessa nella Scheda e nei Reel di quel pezzo, mai due donne con lo stesso pezzo; cambia da un pezzo all'altro). La donna la inventa l'AI per il pezzo: bella ed elegante ma reale, non una modella perfetta. Più mani e negozio veri. Il gioiello parte sempre dalla foto reale. Etichetta "Info sull'AI" su Instagram per contenuti AI realistici
- **Creatività**: l'AI resta libera su luoghi, donne, pose e abiti adatti allo stile del negozio, e non ripete donne e scene recenti. Si fissano solo i divieti, in `skills/_base/divieti.md` (pagina Skill → "Mai nei contenuti"): niente elenchi che rendono i contenuti tutti uguali
- **Frequenza**: 1-2 post/settimana — qualità > quantità
- **Orari**: Martedì / Giovedì / Sabato — fascia oraria DA VERIFICARE (il grafico Insights indica le 18 come ora meno attiva, possibile fuso orario diverso)
- **Hashtag fissi** (sempre presenti): #imoniliravenna #ravenna #romagnastyle

## Visual Identity
- Sfondi: crema/neutri caldi che fanno risaltare i colori dei prodotti; accenti terracotta e oro
- Testi grafici: stile editoriale (serif elegante su fondo crema, es. "Non sono semplici orecchini.") — sono i post più belli del feed. Mai scritte fumetto/neon
- Stile foto/video: luce naturale calda, autentico — no filtri esagerati, no faccia "perfetta" da AI
- Stile Reel: dinamico ma elegante, no effetti pacchiani
- Rubriche: Indossato, Mani al bancone, Pietra della settimana, 3 modi di indossarlo, I colori di Ravenna (mosaico)

## Categorie Prodotto
- **Bijoux**: anelli, orecchini (cerchio, pendente, lobo), collane, bracciali, cavigliere
- **Accessori**: borse, pochette, cinture, sciarpe, cappelli, occhiali, foulard
- **Abbigliamento**: top, camicie, vestiti, gonne, pantaloni, giacche leggere P/E

## Performance Data
→ Vedere `memory/performance_log.json` per dati aggiornati su:
   - Hashtag con più reach storico
   - Caption variant che ha performato meglio
   - Orari con engagement più alto
   - Prodotti che hanno generato più visite in negozio

## Sviluppo
- Skill dei contenuti: `skills/*.md` (guida in `skills/README.md`) — si aggiustano lì, non nel codice
- Ricerca tecniche AI/Instagram: `knowledge/ricerca_marketing_ai_2026.md`; video Higgsfield (modelli API, costi, regole gioielli, protocollo test): `knowledge/higgsfield_video_guida.md`; piano Natale: `docs/piano-natale-2026.md`
- Stato e prossimi passi (condiviso con Hermes): `docs/STATO_PROGETTO.md`
- Test: `python -m pytest tests` (senza chiavi né rete) — da far passare prima di ogni push
- **Impegni legali del sito** (privacy, cookie, vendita a distanza, recesso, immagini IA): `docs/impegni-legali.md` — cosa abbiamo promesso ai clienti e i messaggi pronti. Regole per chi sviluppa: mai dati di clienti nello Studio, nei prompt o nel catalogo; nessun tracker o widget di terzi sul sito senza aggiornare prima `/cookie` e `/privacy`; ogni foto generata dall'AI inviata al sito va marcata `aiGenerated`; se cambia la prassi di vendita, si aggiorna prima `/condizioni-vendita` (vetrina: `src/lib/legal-content.ts`)
