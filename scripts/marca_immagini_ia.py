"""Marca come generate dall'IA (aiGenerated=true) tutte le immagini dei pezzi indicati.

Uso (prova, non scrive nulla):
    python scripts/marca_immagini_ia.py <id-pezzo> [<id-pezzo> ...]
    python scripts/marca_immagini_ia.py --tutti

Per scrivere davvero sul sito online:
    python scripts/marca_immagini_ia.py --tutti --applica

Legge il pezzo dall'API pubblica, conserva src e alt di ogni immagine e imposta
aiGenerated=true (PATCH /api/products/<id>, che il sito protegge con il token di
amministrazione). Il token SHOWCASE_ADMIN_TOKEN e l'indirizzo si leggono dal
.env dello Studio, come fa il server; il token non viene mai stampato.
"""
import argparse
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://monili-vetrina.vercel.app"


def load_env():
    env = {}
    path = ROOT / ".env"
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def http(method, url, token=None, body=None):
    headers = {"User-Agent": "monili-studio/1.0", "Accept": "application/json"}
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if token:
        headers["x-admin-token"] = token
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--tutti", action="store_true", help="tutti i pezzi pubblicati")
    ap.add_argument("--applica", action="store_true", help="scrive sul sito (senza: solo prova)")
    args = ap.parse_args()

    if args.tutti:
        ids = [p["id"] for p in http("GET", f"{BASE}/api/products")["items"]]
    else:
        ids = args.ids
    if not ids:
        sys.exit("Indica almeno un id oppure --tutti.")

    token = ""
    if args.applica:
        token = load_env().get("SHOWCASE_ADMIN_TOKEN", "")
        if not token:
            sys.exit("SHOWCASE_ADMIN_TOKEN non trovato nel .env dello Studio.")

    for pid in ids:
        item = http("GET", f"{BASE}/api/products/{pid}")["item"]
        images = [
            {"src": i["src"], "alt": i["alt"], "aiGenerated": True} for i in item["images"]
        ]
        gia = sum(1 for i in item["images"] if i.get("aiGenerated"))
        print(f"{pid}: {len(images)} immagini, gia' marcate IA: {gia}")
        if not args.applica:
            print("   (prova: nessuna scrittura; aggiungi --applica per scrivere)")
            continue
        out = http("PATCH", f"{BASE}/api/products/{pid}", token=token, body={"images": images})
        marcate = sum(1 for i in out["item"]["images"] if i.get("aiGenerated"))
        print(f"   scritto: {marcate}/{len(out['item']['images'])} immagini marcate IA")


if __name__ == "__main__":
    main()
