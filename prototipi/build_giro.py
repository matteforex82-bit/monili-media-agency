"""Build the 'Pietra della settimana' prototype. If a clip is given, its frames replace the stand-in photo."""
import base64, json, pathlib, subprocess, sys, tempfile
here = pathlib.Path(__file__).parent
out_local = pathlib.Path(sys.argv[1])
clip = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else None
def uri(p):
    return "data:image/jpeg;base64," + base64.b64encode(pathlib.Path(p).read_bytes()).decode()
frames = []
if clip and clip.exists():
    tmp = pathlib.Path(tempfile.mkdtemp())
    n = 48
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(clip)]).decode().strip())
    subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", str(clip), "-vf",
        f"fps={n/dur:.4f},crop='min(iw,ih)':'min(iw,ih)',scale=640:640", "-q:v", "6", str(tmp / "f%03d.jpg")])
    frames = [uri(p) for p in sorted(tmp.glob("f*.jpg"))[:n]]
src = (here / "giro.src.html").read_text(encoding="utf-8")
page = src.replace("__STILL__", uri(here / "img" / "anello.jpg")).replace("__FRAMES__", json.dumps(frames))
(here / "pietra-della-settimana.html").write_text(page, encoding="utf-8")
out_local.parent.mkdir(parents=True, exist_ok=True)
out_local.write_text('<!doctype html>\n<html lang="it">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n<style>body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n</head>\n<body>\n' + page + '\n</body>\n</html>\n', encoding="utf-8")
print(len(frames), "frames,", len(page)//1024, "KB")
