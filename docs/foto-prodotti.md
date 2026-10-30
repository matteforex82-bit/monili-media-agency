# Foto dei prodotti per il sito vetrina

Regola (29/10/2026): **un formato uguale per tutti i pezzi**: verticale 4:5, fondo avorio. Le immagini di Instagram sono extra.

## Le foto di ogni pezzo: 2 o 3, sempre in quest'ordine

1. **Pulita "da studio"** (AI, dalla tua foto): il pezzo da solo su fondo avorio. È la copertina della card in Home. Prima di pubblicarla controlla che sia fedele: l'AI a volte cambia un dettaglio (a maggio una goccia blu è uscita ovale).
2. **Indossata** (AI): una donna per pezzo, bella ed elegante ma reale (età, corpo e viso da persona normale, non da modella), come se per quel pezzo avessimo ingaggiato una modella. La inventa l'AI per quel pezzo (linea guida in `skills/_base/donne.md`), diversa dalle donne usate di recente; luogo e posa li sceglie lei. Le cose da non mostrare mai sono in `skills/_base/divieti.md`. Il Reel dello stesso pezzo, fatto con "Fai il Reel di questo pezzo", usa la stessa donna.
3. **Foto vera ripulita** (nessuna AI sul pezzo): scontorno fatto sul PC, fondo avorio uguale alle altre, luce, bilanciamento del bianco e contrasto sistemati. Lo Studio la spunta **solo se lo scontorno è pulito**; se il pezzo tocca il bordo della foto (oggetto attaccato o pezzo tagliato) resta senza spunta e lo Studio scrive il motivo. Se viene male, il pezzo esce con 2 foto.

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
