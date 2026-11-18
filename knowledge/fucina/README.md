# Fucina dei prompt: la conoscenza

Questi file entrano nelle richieste che lo Studio fa all'AI quando scrive i prompt (`prompt_lab.model_knowledge`):
il file del **modello scelto** e la **ricetta del tipo di pezzo**. Si modificano come testo.

Ogni regola ha un'etichetta, così non scambiamo un'ipotesi per un fatto:
- `[verificato: data, dove]`: visto nei nostri test, con voto o clip.
- `[fonte: nome]`: preso da documentazione o guide, non ancora provato da noi.
- `[ipotesi]`: da provare. Passa a verificato solo dopo 2-3 risultati coerenti e l'ok di Matteo.

Stato: primo seme del 18/11/2026. Da completare con le guide ufficiali di Seedream e Seedance e con le prove vere.
