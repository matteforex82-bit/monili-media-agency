"""Materiali locali per un test manuale Higgsfield su una ripresa continua."""

from pathlib import Path
import zipfile

import reel_studio
from reel_blender import format_time
from reel_seedance_kit import prompts

MODEL_GUIDE = "https://higgsfield.ai/creator-hub/help-center/ai-models/how-do-i-use-seedance"


def package(
    directory: Path, source: Path, draft: dict, preview: dict, shot_index: int, photos: list[Path],
) -> Path:
    shots = draft["package"]["shots"]
    shot = shots[shot_index]
    start = preview.get("timeline_start_ms", shots[shot_index - 1]["end_ms"] if shot_index else 0)
    end = preview.get("timeline_end_ms", shot["end_ms"])
    plate = directory / "riferimento-blender.mp4"
    reel_studio._run_ffmpeg([
        "-i", str(source), "-map", "0:v:0", "-an", "-sn", "-dn",
        "-vf", "scale=720:1280:force_original_aspect_ratio=decrease:force_divisible_by=2,"
        "pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p",
        *reel_studio.X264_ARGS, str(plate),
    ])

    instructions = prompts(shots, len(photos))[shot_index]
    source_photo = instructions["product_reference"]
    photo_note = (
        f"La regia indica come prima referenza la foto {source_photo} in `foto-prodotto/`."
        if source_photo else "Aggiungi una foto reale del pezzo per poter verificare la fedeltà del risultato."
    )
    guide = f"""# Prova Higgsfield · {draft['product']}

**Inquadratura {shot_index + 1} · {shot['framing']}**

Timeline del Reel · {format_time(start)}–{format_time(end)}

Clip di riferimento · {format_time(preview['duration_ms'])}

## Materiali e impostazioni

- `riferimento-blender.mp4` è la ripresa approvata, in 9:16 e senza audio. Usa una sola ripresa continua.
- {photo_note} Prepara il primo fotogramma con `composizione.jpg` e `foto-en.txt`, oppure usa una foto reale con la stessa posa e lo stesso taglio. Confrontalo con il pezzo.
- In Higgsfield scegli Seedance in una modalità che accetta insieme immagini e video di riferimento. Allega la clip Blender, il primo fotogramma preparato e i riferimenti reali del pezzo. Copia `prompt-en.txt` come prompt video. [Guida Seedance]({MODEL_GUIDE})
- Controlla la durata minima del modello scelto. Se il riferimento è troppo corto, esporta da Blender la stessa ripresa con margine prima o dopo il gesto. Rifila il risultato ai timecode del montaggio.
- Tieni la musica nel montaggio e usa il primo test per valutare soltanto la ripresa.

## Regia da conservare

- Camera · {shot['camera']}
- Luce · {shot['lighting']}
- Azione · {shot['action']}
- Taglio · {shot['cut']}

{draft['package']['higgsfield']}

## Confronto in AI Studio

Ricarica il risultato sotto la stessa previsualizzazione in Reel Blender. Confronta i primi, i medi e gli ultimi fotogrammi utili.

- Prodotto · colore, proporzioni, ricami o pietre, zip e chiusure.
- Camera · campo iniziale e finale, direzione del movimento.
- Azione · posa, mani, gesto e punto in cui deve completarsi.
- Montaggio · individua il punto di ingresso e uscita da riportare in timeline.
"""
    archive = directory / "prova-higgsfield.zip"
    composition = directory / "composizione.jpg"
    reel_studio._frame_at(plate, 0, composition)
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as output:
        output.write(plate, "riferimento-blender.mp4")
        output.writestr("LEGGIMI.md", guide)
        output.writestr("prompt-en.txt", instructions["video_en"])
        output.writestr("foto-en.txt", instructions["photo_en"])
        output.write(composition, "composizione.jpg")
        for index, photo in enumerate(photos, 1):
            output.write(photo, f"foto-prodotto/foto-{index}{photo.suffix}")
    return archive
