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
- Da iPhone sulla stessa rete Wi-Fi: usa l'URL `iPhone (stesso Wi-Fi)` stampato dallo script
- Da iPhone ovunque (4G, negozio, fuori casa): usa l'URL `iPhone (ovunque, Tailscale)`, vedi sotto

Il frontend chiama il backend sullo stesso indirizzo con cui apri la pagina (porta 8000), quindi lo stesso avvio funziona per tutti e tre i casi.

## Usarla dal telefono ovunque (Tailscale)

Tailscale crea una rete privata tra il PC e il telefono: l'app resta sul PC, non è visibile su internet, e il telefono la raggiunge anche in 4G. Gratis per uso personale.

**Modo rapido**: sul PC fai doppio clic su `Configura Telefono.bat` (nella cartella del progetto) e conferma i permessi di amministratore. Fa da solo i passi 1, 3 e il firewall qui sotto; tu devi solo accedere a Tailscale quando si apre il browser, e poi installare l'app Tailscale sull'iPhone con lo stesso account.

A mano, una volta sola:

1. Sul PC: installa Tailscale da https://tailscale.com/download/windows e accedi (es. con Google)
2. Sull'iPhone: installa l'app Tailscale dall'App Store e accedi **con lo stesso account**
3. Sul PC: Impostazioni → Sistema → Alimentazione → "Sospensione" su **Mai** quando è collegato alla corrente (lo schermo può spegnersi)
4. Avvia con `.\scripts\start-local.ps1`: ora stampa anche l'indirizzo Tailscale (`http://100.x.y.z:3000`)
5. Sull'iPhone, con Tailscale attivo, apri quell'indirizzo in Safari → Condividi → **Aggiungi alla schermata Home**: diventa un'icona come un'app

Se dal telefono la pagina non si apre, Windows sta bloccando le porte sulla rete Tailscale. Da PowerShell **come amministratore**, una volta sola (apre le porte solo ai dispositivi del tuo Tailscale, non a internet):

```powershell
New-NetFirewallRule -DisplayName "Monili via Tailscale" -Direction Inbound -Protocol TCP -LocalPort 3000,8000 -RemoteAddress 100.64.0.0/10 -Action Allow
```

Le foto si caricano direttamente dal rullino o dalla fotocamera dell'iPhone (anche HEIC) e finiscono in `MoniliStorage` sul PC.

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

- Render oggi **non ha password**: chi conosce l'indirizzo può lanciare generazioni con le tue chiavi. Se usi la modalità locale, sospendi i servizi `monili-backend` e `monili-frontend` dal dashboard Render (Settings → Suspend) finché non c'è una password.
- Se usi l'app locale da iPhone, i file master restano sul portatile.
- Il backend locale deve restare aperto durante la generazione.
- Images 2 via OpenRouter puo richiedere diversi minuti per completare le immagini.
