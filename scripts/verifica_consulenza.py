"""Verifica J07: la consulenza e' accesa (o spenta) sul sito online.

Uso:
    python scripts/verifica_consulenza.py            # controlla il sito online
    python scripts/verifica_consulenza.py --atteso spenta

Solo letture HTTP, nessun dato scritto. Con --atteso accesa (default) controlla
che, dopo aver inserito il link Calendly su Vercel e ripubblicato, compaiano:
/consulenza (200) con un link https://calendly.com/..., la voce nel menu, i
paragrafi su Calendly in privacy e cookie. Con --atteso spenta controlla il
contrario (stato attuale prima di J07). In entrambi i casi controlla che il
link a Calendly sia un semplice collegamento: nessuno script o iframe di terzi.
"""
import argparse
import re
import sys
import urllib.error
import urllib.request

BASE = "https://monili-vetrina.vercel.app"
THIRD_PARTY = ("assets.calendly.com", "calendly.com/assets", "widget.js")


def get(path):
    req = urllib.request.Request(BASE + path, headers={"User-Agent": "monili-check/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--atteso", choices=["accesa", "spenta"], default="accesa")
    on = ap.parse_args().atteso == "accesa"

    risultati = []

    def check(nome, ok):
        risultati.append(ok)
        print(("OK   " if ok else "FAIL ") + nome)

    st, cons = get("/consulenza")
    check(f"/consulenza risponde {'200' if on else '404'} (ottenuto {st})", st == (200 if on else 404))
    link = re.findall(r"https://calendly\.com/[^\"'\s<>]+", cons)
    if on:
        check("/consulenza contiene un link https://calendly.com/...", bool(link))
        if link:
            print("     link trovato:", link[0])

    st, home = get("/")
    check(f"home risponde 200 (ottenuto {st})", st == 200)
    voce_menu = bool(re.search(r'href="/consulenza"', home))
    check("voce/CTA verso /consulenza nella home " + ("presente" if on else "assente"), voce_menu == on)

    # Nella privacy compare il nome Calendly; nella pagina cookie solo «il calendario di prenotazione».
    for pagina, marcatore in (("/privacy", "Calendly"), ("/cookie", "calendario di prenotazione")):
        st, html = get(pagina)
        testo = re.sub(r"<[^>]+>", " ", html)
        check(f"{pagina} 200 (ottenuto {st})", st == 200)
        check(f"{pagina}: paragrafo sul calendario " + ("presente" if on else "assente"), (marcatore in testo) == on)

    st, sitemap = get("/sitemap.xml")
    check("sitemap: /consulenza " + ("presente" if on else "assente"), ("/consulenza" in sitemap) == on)

    tutto = cons + home
    terzi = [t for t in THIRD_PARTY if t in tutto]
    check("nessun widget/script di Calendly caricato in automatico" + (f" (trovati: {terzi})" if terzi else ""), not terzi)
    check("nessun iframe di Calendly", "<iframe" not in tutto.lower() or "calendly" not in tutto.lower())

    print()
    print("TUTTO OK" if all(risultati) else "CI SONO PROBLEMI: vedi i FAIL sopra")
    sys.exit(0 if all(risultati) else 1)


if __name__ == "__main__":
    main()
