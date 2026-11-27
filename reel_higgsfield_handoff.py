"""Materiali locali per un test manuale Higgsfield su una ripresa continua."""

from pathlib import Path
import zipfile

import reel_studio
from reel_blender import format_time

MODEL_GUIDE = "https://higgsfield.ai/creator-hub/help-center/ai-models/how-do-i-use-kling"

PROMPT = """Create a single continuous shot using the real product image as the source of truth.
Follow the intended framing and gentle timing of the supplied video reference where the selected mode supports it.
Keep the exact product silhouette, construction, color, pattern, material appearance and hardware from the product references.
Keep hands, pose and camera movement minimal and stable. Preserve the initial and final composition.
No cuts, titles, watermarks, music, added decorations or changes to the product.
"""


def package(
    directory: Path, source: Path, draft: dict, preview: dict, shot_index: int, photos: list[Path],
) -> Path:
    shots = draft["package"]["shots"]
    shot = shots[shot_index]
    start = shots[shot_index - 1]["end_ms"] if shot_index else 0
    end = shot["end_ms"]
    plate = directory / "riferimento-blender.mp4"
    reel_studio._run_ffmpeg([
        "-i", str(source), "-map", "0:v:0", "-an", "-sn", "-dn",
        "-vf", "scale=720:1280:force_original_aspect_ratio=decrease:force_divisible_by=2,"
        "pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p",
        *reel_studio.X264_ARGS, str(plate),
    ])

    source_photo = (shot.get("design") or {}).get("reference_photo", 1)
    photo_note = (
        f"La regia indica come prima referenza la foto {min(source_photo, len(photos))} in `foto-prodotto/`."
        if photos else "Allega tu una foto reale del pezzo o un fotogramma in posa verificato contro le foto reali."
    )
    guide = f"""# Prova Higgsfield · {draft['product']}

**Inquadratura {shot_index + 1} · {shot['framing']}**

Timeline del Reel · {format_time(start)}–{format_time(end)}

Clip di riferimento · {format_time(preview['duration_ms'])}

## Materiali e impostazioni

- `riferimento-blender.mp4` è la ripresa approvata, in 9:16 e senza audio. Usa una sola ripresa continua.
- {photo_note} Scegli un’immagine coerente con la posa e l’angolo di partenza. Le foto del prodotto guidano il controllo della fedeltà.
- `prompt-en.txt` è il prompt di partenza. In Higgsfield scegli una modalità che accetti immagine e video di riferimento. Motion Control segue soprattutto il movimento visibile di un soggetto. Se la clip Blender è un piano 2D o prevale il movimento di camera, prova una modalità video-reference e verifica che lo segua. [Guida Higgsfield]({MODEL_GUIDE})
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
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as output:
        output.write(plate, "riferimento-blender.mp4")
        output.writestr("LEGGIMI.md", guide)
        output.writestr("prompt-en.txt", PROMPT)
        for index, photo in enumerate(photos, 1):
            output.write(photo, f"foto-prodotto/foto-{index}{photo.suffix}")
    return archive
