# Foto dei prodotti per il sito vetrina

Regola (29/10/2026): **un formato uguale per tutti i pezzi**: verticale 4:5, fondo avorio. Le immagini di Instagram sono extra.

## Le foto di ogni pezzo: dipendono da cosa stai pubblicando (dal 02/11/2026)

Regola di marketing (Matteo, 02/11/2026): mai due foto "da catalogo" quasi uguali, una vera e una AI, perché mettono in evidenza le differenze dell'AI. La foto vera dice **com'è** il pezzo, l'AI dice **come sta addosso**. Lo Studio capisce la categoria dall'analisi e fa solo le foto che servono:

| Pezzo | Foto per il sito, in quest'ordine |
|---|---|
| **Abbigliamento** | foto vera ripulita (copertina) · indossata AI a figura intera · seconda indossata AI da un altro angolo, con un altro abbinamento e in un altro luogo |
| **Gioielli e bijoux** | foto vera ripulita (copertina) · indossata AI in primo piano (orecchio, mano, collo o polso) · dettaglio vero ripulito, se lo carichi |
| **Accessori** | foto vera ripulita (copertina) · indossata AI a mezzo busto (si capisce quanto è grande) · dettaglio vero ripulito, se lo carichi |

- **Foto vera ripulita** (nessuna AI sul pezzo): scontorno fatto sul PC, fondo avorio, luce, bilanciamento del bianco e contrasto sistemati. Lo Studio la mette in copertina **solo se lo scontorno è pulito**. Se viene male, la copertina diventa la foto **catalogo AI** (fatta solo in quel caso) e la foto vera resta in fondo, senza spunta, con il motivo.
- **Indossate** (AI): una donna per pezzo, bella ed elegante ma reale, sempre la stessa nelle due indossate e nel Reel di quel pezzo (linea guida in `skills/_base/donne.md`, divieti in `skills/_base/divieti.md`). Le inquadrature per categoria sono in `categorie.py` (`SHOT_GUIDE`).
- **Dettaglio vero** (facoltativo, in "Nuovo pezzo" → "Aggiungi il dettaglio"): la pietra, la chiusura, il cuoio da vicino. Ripulito come la foto principale, mai ridisegnato dall'AI.
- Risparmio: quando la foto vera viene pulita, una generazione AI in meno per pezzo.

## Come scattare la foto vera con il telefono

- Niente oggetti vicini o attaccati al pezzo: nella prova una scopa appoggiata alla manica è rimasta nello scontorno.
- Il pezzo intero nell'inquadratura, con un po' di margine intorno.
- Un foglio bianco o crema dietro o sotto, luce da finestra, mai flash.
- Ferma e a fuoco: una foto mossa o sfocata non si salva.

## Reel

I fotogrammi AI del Reel non si pubblicano come foto. Sul sito vanno solo il video e la copertina (sala Reel e "Guardalo indossato" nella scheda del pezzo). Il Reel non serve per ogni pezzo.

## Peso

Max 4 foto per invio (limite Vercel); lo Studio avvisa se la scheda supera 4,2 MB.

## Come funziona la pulizia (per chi tocca il codice)

- Codice in `photo_cleanup.py`, chiamato da `main.create_real_photo_image`; se qualcosa va storto resta il semplice ritaglio 4:5, non spuntato.
- Modello BiRefNet-general (ONNX, ~1 GB) in `<MONILI_STORAGE_DIR>/models/`: si scarica da solo la prima volta, con controllo del checksum. `CUTOUT_MODEL_AUTO_DOWNLOAD=0` per non scaricarlo mai.
- Circa 10–20 secondi a foto sul PC, gratis.
- Niente `rembg`: su questo PC Windows blocca le DLL di `scipy`, che rembg usa. Bastano `onnxruntime` e `numpy`.
