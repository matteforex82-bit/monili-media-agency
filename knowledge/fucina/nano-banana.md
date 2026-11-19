## Conoscenza: Nano Banana Pro (Gemini 3 Pro Image) e Nano Banana 2
Etichette: [verificato] = visto nei test; [fonte] = ricerca, non ancora provato; [ipotesi].
- Ragiona sempre prima di disegnare (modalità "thinking" non disattivabile). [fonte: report 13/11]
- Struttura: soggetto e materiali, azione, luogo, inquadratura e ottica, luce e pellicola, vincoli o testo tra virgolette. Gli edit partono con un verbo diretto: "Replace only the leather strap...", "Remove...". [fonte: report 13/11]
- Blocco di identità esplicito: "Keep the person's facial features and the ring prongs exactly the same as Image 1." [fonte: report 13/11]
- Fino a 14 riferimenti, ma solo circa 6 oggetti ad alta fedeltà e 5 volti coerenti. [fonte: report 13/11, Google AI Studio]
- Per il fotorealismo della pelle citare hardware e pellicola reali: "shot on medium format film", "Fujifilm colour science", "fine 35mm grain", luce "soft north window light". Evitare luci contraddittorie ("dark moody" + "bright cheerful"). [fonte: report 13/11]
- I filtri sono severi: può rifiutare foto di moda legittime (gambe, scollature). Se blocca, riprovare con Seedream. [fonte: report 13/11; Playbook A2]
- Sulla foto delle varianti (rotolo di 12 anelli) nessuna AI è identica al vero e Nano Banana trasforma l'azzurro in turchese: serve il controllo di Matteo. [verificato: 07/11, Studio]
- Gioiello su mano: "Keep the piece exactly the same as Image 1, including shape, stone, finish. Place it on the ring finger of a relaxed hand on a linen surface, soft north window light, 85mm, shallow depth of field, natural skin texture." [fonte: Playbook J2, da provare]
- Costo su fal: 1K e 2K stesso prezzo (0,15 $), quindi iterare in 2K. [fonte: report 13/11] Su Higgsfield da 1 a 4 crediti (2 a 1K e 2K, 4 a 4K); supporta il 4:5. [fonte: ricerca 19/11]
- Pezzo vero sulla donna in due passi: prima la donna senza gioielli, poi si innesta il pezzo con misure e ombra di contatto: "Place the exact necklace from Image 2 at the neckline of the woman in Image 1, matching the real-world scale shown in Image 3. Keep stone colour, mineral veining, bezel setting and silver chain links 100% identical to Image 2. Add a natural soft contact shadow." Senza Soul ID il volto deriva sulle serie lunghe. [fonte: ricerca 19/11]
**Versioni e scelta** [fonte: ricerca A 19/11, changelog Higgsfield 16/11, Google AI Studio, test Runware, Masonry e On-Model; non ancora provato da noi]
- Su Higgsfield: Pro, 2.1 (dal 06/10), 2 e 2 Lite (solo bozze a 1K). Pro: 4K nativo, 4:5 nativo, codici colore HEX, @Elements; fino a 14 riferimenti ma al massimo 6 oggetti, 5 personaggi e 3 stili. La 2.1 e la 2: 10 oggetti e 4 personaggi.
- Anelli e capi ricamati: usare Pro, non la 2. La 2 ha sbagliato il numero di griffe (oltre 4 invece di 4), ha schiacciato le trame tessili e reso illeggibili i ricami piccoli. Controllare sempre griffe, bottoni e tasche inventate.
- La 2.1 deriva dopo 1-2 modifiche in fila (sfondo schiarito con dominante rosa): ripartire dalla foto originale.
- Pro ogni tanto ignora i riferimenti (10-20% dei run): rigenerare con gli stessi file e numerare "Reference Image 1 / 2".
- Divieti scritti in positivo ("clean bare surface", non "no clutter"): i primi dettagli del prompt pesano di più, quindi pezzo e vincoli in apertura.
- Se la foto esce sfocata o "fantasma" a 2K/4K con più riferimenti: fare 1K, poi upscale. Se il filtro blocca un capo: scrivere "wearing the garment from Reference Image 1" invece di "swap / replace", niente nomi di persone reali.
- Non cambiare prompt e riferimento insieme tra due prove: non si capisce più cosa ha causato la deriva.
**Da verificare [dubbio]**: costo in crediti della 2.1; "Banana Placement"; una ricerca dà "14 oggetti stabili", contro i nostri circa 6 ad alta fedeltà (la documentazione Google dice 6 su Pro).
Per approfondire: `knowledge/nano_banana_2_prompts.md` (linee guida già nei prompt automatici), `Learn Higgsfield/docs/Prompting Avanzato Gioielleria e Moda.md` (sezione 3).
