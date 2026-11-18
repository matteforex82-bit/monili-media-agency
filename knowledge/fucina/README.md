# Fucina dei prompt: la conoscenza

Questi file entrano nelle richieste che lo Studio fa all'AI quando scrive i prompt (`prompt_lab.model_knowledge`):
il file del **modello scelto** e la **ricetta del tipo di pezzo**. Si modificano come testo. Ogni file è corto di proposito:
finisce per intero dentro il prompt.

Etichette, perché un'ipotesi non diventi un fatto:
- `[verificato: data, dove]`: visto nei nostri test (cartella `Learn Higgsfield`, prove di Matteo) o scelta del negozio.
- `[fonte: ...]`: preso dalla ricerca (`Learn Higgsfield/docs/Prompting Avanzato Gioielleria e Moda.md`, rivista il 13/11 con 36 correzioni) o dalle guide Higgsfield; non ancora provato da noi.
- `[ipotesi]`: da provare. Passa a verificato dopo 2-3 risultati coerenti e con l'ok di Matteo.
Quando un test contraddice la ricerca, vince il test.

| File | Contenuto | Collegato alla Fucina |
|---|---|---|
| `seedream.md` | foto da foto vera (Seedream 5.0 Flash/Lite/Pro) | sì |
| `nano-banana.md` | Nano Banana Pro e 2 | sì |
| `gpt-image.md` | GPT Image 2 / 2.5 / 2.6 | sì |
| `seedance.md` | video Seedance 2.5 | sì (scene video dell'abbigliamento) |
| `kling.md`, `genjutsu.md`, `flux.md` | conoscenza pronta | non ancora scelti nella Fucina |
| `ricetta-bijoux.md`, `-abbigliamento.md`, `-accessori.md` | cosa fare per tipo di pezzo | sì |
| `modella-aurora.md` | lo slot `@MODELLA` e la modella Monili-Aurora | no: è una nota per Matteo, non entra nei prompt |

Stato: 18/11/2026. Sorgenti: `C:\Users\matte\Desktop\PROGETTI AI\Learn Higgsfield` (PROMPT_PLAYBOOK, PROVE_REEL_SEEDANCE,
GENJUTSU_PROVE_E_RICETTA, costi_test.csv, report Prompting Avanzato). Ancora da leggere dalla cartella: PIANO_DATASET_MODELLA
(per il training) e le skill generiche Higgsfield; non riguardano i prompt.
