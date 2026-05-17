# Modalita Locale Monili

Questa modalita salva foto, output, cronologia e memoria sul portatile invece che nello storage temporaneo di Render.

## Avvio rapido Windows

Da PowerShell, nella cartella del progetto:

```powershell
.\scripts\start-local.ps1
```

Lo script mostra in console anche l'URL esatto da aprire su iPhone, per esempio:

```text
iPhone:   http://192.168.1.20:3000
API URL:  http://192.168.1.20:8000
```

Storage predefinito:

```text
C:\Users\<utente>\MoniliStorage
```

Per scegliere una cartella diversa:

```powershell
.\scripts\start-local.ps1 -StorageDir "C:\Users\matte\Desktop\MoniliStorage"
```

## URL

- Dal portatile: `http://localhost:3000`
- Da iPhone sulla stessa rete Wi-Fi: usa l'URL `iPhone:` stampato dallo script

Per trovare l'IP del portatile:

```powershell
ipconfig
```

Cerca l'indirizzo IPv4 della rete Wi-Fi, per esempio `192.168.1.20`.

## Cosa viene salvato

```text
MoniliStorage/
  input/      foto caricate
  output/     immagini generate, testi, manifest e cronologia
  memory/     performance_log.json
```

## Note importanti

- Render resta usabile come backup online.
- Se usi l'app locale da iPhone, i file master restano sul portatile.
- Il backend locale deve restare aperto durante la generazione.
- Images 2 via OpenRouter puo richiedere diversi minuti per completare le immagini.
