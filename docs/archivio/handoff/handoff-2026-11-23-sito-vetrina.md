# Handoff

> Generated: 2026-11-23
> Project: sito vetrina `C:\Users\matte\Desktop\PROGETTI AI\Ecosistema Monili` (repo `monili-vetrina`, app in `apps/web`, branch `master`); questa cartella (`monili-deploy-temp`, Studio, ramo `studio-percorso-unico`) contiene solo i documenti.
> Session summary: favicon dalla monogramma del logo e sezione «Dicono di noi» con recensioni Google vere su un cartellino appeso e quattro ragazze disegnate che si alternano; grafica completa e online, mancano recensioni (ce ne sono solo 3, servono almeno 5).

## Goal
Mostrare nel sito le vere recensioni Google in modo bello e coerente col brand, senza widget o tracker di terzi (`docs/impegni-legali.md`). Decisione di Matteo (23/11): **almeno 5 recensioni che scorrono, nessuna da 1 stella nel sito**.

## Current State
**Working (online, deploy Vercel riuscito, ultimo commit `1bfbb9c`):**
- Favicon «iM» + fascia pesca: `apps/web/src/app/favicon.ico` (RGBA!), `icon.png`, `apple-icon.png`.
- Sezione recensioni in home prima di `VisitBlock`: fascia `--stage` (come footer), cartellino crema in rilievo con angolo piegato, testo scritto lettera per lettera, 4 ragazze SVG che ruotano a ogni cambio, nav con frecce e trattini, auto-advance 4,5 s, reduced-motion safe.

**Open:**
- Solo 3 recensioni (Alice Bosi, Roberta Ramari, Elena Giovannini, tutte 5 stelle): Maps anonimo mostra solo quelle su 29 totali.
- Punteggio 4,7 e conteggio 29 scritti a mano in `googleReviewsSummary`.
- Icona Google: aggiornamento in 1-2 settimane; richiesta indicizzazione in Search Console da fare a mano.

## Files in Play
| File | Why |
|---|---|
| `apps/web/src/lib/google-reviews.ts` | Dati reali + `googleReviewsSummary`; qui si aggiungono le recensioni |
| `apps/web/src/components/google-reviews.tsx` | Server component: titolo, punteggio, nota, mette `featured` per primo |
| `apps/web/src/components/google-reviews-stage.tsx` | Client: typing, rotazione `step`, nav, IntersectionObserver. Usa `useSyncExternalStore` per reduced-motion (ESLint `set-state-in-effect` vieta setState sincrono negli effect) |
| `apps/web/src/components/google-reviews-girls.tsx` | Le 4 ragazze, array `girls` in ordine di apparizione: GirlBun, GirlClassic, GirlCurly, GirlScarf |
| `apps/web/src/app/vetrina.css` | Blocco `.v-gr*` in fondo al file (`--gr-black: var(--stage)`) |
| `apps/web/src/app/page.tsx` | Monta `<GoogleReviews />` prima di `<VisitBlock />` |
| `docs/STATO_PROGETTO.md` (questa repo) | Sezione «Sito vetrina: icona e recensioni Google» riscritta con lo stato finale |

## What Has Been Tried (and Why It Failed)
- **favicon.ico in RGB**: build Vercel fallito («The PNG is not in RGBA format!»). Salvarlo da un'immagine RGBA.
- **Ritaglio della «M» dal logo**: il primo ritaglio includeva la «o»; risolto con componenti connesse (flood fill).
- **Classe `.v-gr__head` usata sia dall'header sia dal gruppo SVG della testa**: rinominata `.v-gr__headg`.
- **Widget Google / Places API**: scartati, violano la promessa «nessun terzo» e servirebbe una chiave.
- **Medaglione pesca per la ragazza**: tolto su richiesta di Matteo; ora la ragazza è disegnata direttamente sul cartellino. Il nero più profondo `#0e0c09` per la fascia: sostituito con `--stage` (#16130f) per uguagliare footer e «Vieni a trovarci».
- **Heredoc bash con `'''` e CSS lunghi**: il tool ha dato «unexpected EOF»; usare Write per i file lunghi e script Python in file.
- **Browser pane in background**: i timer rallentano, il testo «scritto» sembra fermo nei test; controllare `document.querySelector('.v-gr__live').textContent.length`.

## Current Best Theory
Soluzione statica (testo copiato a mano + link a Google): funziona e rispetta le promesse legali. Per le recensioni mancanti serve Matteo (le vede tutte da Business Profile o da Maps loggato).

## Next Steps
1. Chiedere a Matteo di incollare almeno 2-4 recensioni vere in più (testo, nome, stelle), escluse quelle da 1 stella per la selezione del sito.
2. Aggiungerle in `apps/web/src/lib/google-reviews.ts` (una riga ciascuna, testo identico all'originale, `author` unico perché usato come key). Con 5+ la rotazione delle 4 ragazze continua da sola.
3. Prima del push, dal repo del sito: `npx tsc --noEmit`, `npx eslint src/components/google-reviews*.tsx`; controllare a occhio desktop e telefono con `preview_start vetrina-web` (`.claude/launch.json`).
4. Commit con `Co-Authored-By`, push su `master`, poi `gh api repos/matteforex82-bit/monili-vetrina/commits/master/status --jq .state` e curl della home per verificare.
5. Aggiornare `rating`/`count` in `googleReviewsSummary` se cambiano; ricordare a Matteo la richiesta di indicizzazione in Search Console.
6. Valutare se una ragazza deve coincidere con Aurora (testimonial fissa) e `/impeccable init` per creare `PRODUCT.md` nel repo del sito.

## Key Constraints
- Mai modificare o inventare parole di recensioni; niente date; niente `AggregateRating` JSON-LD. Il punteggio 4,7 e il link «Leggi tutte su Google» restano reali anche se sul sito non mostriamo le recensioni da 1 stella.
- Nessun widget/tracker di terzi senza aggiornare `/cookie` e `/privacy`.
- Next.js di questa versione ha breaking changes: leggere `node_modules/next/dist/docs/` prima di API nuove (`apps/web/AGENTS.md`).
- Matteo vuole la pubblicazione online diretta dopo l'anteprima; commit con `Co-Authored-By`.
- Impeccable: vietati eyebrow/kicker sopra i titoli e glifi unicode al posto delle icone; manca `PRODUCT.md`.
- Questa repo (Studio) ha modifiche non committate di altre sessioni (`api/server.py`, `main.py`, `categorie.py`, ...): non toccarle; `HANDOFF.md` è un altro handoff (PRD prompt completi del 20/11), non sovrascriverlo.

## Memory Pointers
- Observations: #2501 (repo sito e logo individuati).
- Search: `favicon monili`, `google reviews vetrina`, `cartellino ragazze`.
