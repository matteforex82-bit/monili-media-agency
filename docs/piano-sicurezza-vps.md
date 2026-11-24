# Piano: mettere in sicurezza la VPS prima dei dati fiscali (bozza 24/11/2026)

Stato: **solo piano. Nessun comando è stato eseguito per applicarlo.** Riguarda le voci 35 e 36 di `docs/interventi-richiesti-matteo.md` e `docs/prd-fiscale.md` §10. Macchina: `hermes-matteo-assistant`, Ubuntu 24.04, indirizzo Tailscale 100.124.146.32.

## Regole di lavoro
- **Ogni passo con modifiche parte solo dopo un ok esplicito di Matteo in chat** («sì, passo N»). I passi di sola lettura no.
- Matteo ha sempre **una seconda finestra SSH aperta** durante le modifiche all'accesso, e sa dove trovare la **console di emergenza** del fornitore della VPS (pannello web) per rientrare se qualcosa va storto. **Passo 0 obbligatorio: verificare di avere l'accesso a quella console.**
- Si fa **una modifica alla volta**, con prova e ritorno indietro descritto. Prima di toccare un file di configurazione se ne salva una copia datata.
- Le password non si incollano in chat. Le chiavi private non lasciano il PC.

## Passo 0 — Prerequisiti (Matteo, 10 minuti)
1. Aprire il pannello del fornitore della VPS e controllare di poter entrare nella **console di emergenza (VNC o seriale)** e di conoscere la password o il metodo per usarla. Senza questo non si cambia l'accesso.
2. Verificare che Tailscale su PC e iPhone sia attivo (già visibile oggi) e che l'iPhone entri in SSH almeno una volta con un client (facoltativo ma utile come seconda via).
3. Decidere il **nome dell'utente di amministrazione** al posto di `root` (esempio: `matteo`).

## Esito del passo 0 (24/11/2026)
Il pannello del fornitore (sembra Contabo, istanza `vmi3431404`, Cloud VPS 10, regione UE, 173.212.242.57) ha: **VNC Control** (console di emergenza), **Rescue System**, **Manage Firewall** (firewall del fornitore, un'ulteriore difesa dall'esterno), **Manage Snapshots** (copia dell'intero disco). **Da non toccare:** Reinstall e Reset credentials. Da fare ancora: aprire VNC Control una volta per vedere che funzioni; **creare uno snapshot prima del passo 2** (controllando numero massimo e costo nel pannello); ricordare la password di root per la console, che non dipende da SSH.

## Passo 1 — Lettura: stato attuale (nessuna modifica)
Script: `back-office/vps/passo1-lettura-accessi.sh`, lanciato da Matteo come il precedente.
Con l'ok di Matteo: controllare chiavi già autorizzate (`authorized_keys`: solo conteggio e impronte), impostazioni effettive di SSH (`sshd -T`, inclusi i file in `sshd_config.d/`, perché `cloud-init` può forzare la password), utenti con shell, appartenenza al gruppo `docker`, regole di rete attive. **Esito atteso:** sapere se la chiave `id_ed25519` del PC è già autorizzata e chi altro può entrare.

## Passo 2 — Chiave SSH funzionante e utente di amministrazione
1. Creare l'utente `matteo` (o il nome scelto) con permessi `sudo`.
2. Copiare la **chiave pubblica** del PC (e, se Matteo vuole, una seconda, di riserva, tenuta fuori dal PC) tra le chiavi autorizzate di quell'utente.
3. **Prova:** da una nuova finestra, entrare come `matteo` con la sola chiave e lanciare `sudo -v`. **Non si procede finché non funziona.**
**Ritorno indietro:** l'accesso vecchio non è ancora toccato.

## Passo 3 — Firewall che lascia entrare solo Tailscale (UFW)
Ordine che evita di chiudersi fuori:
1. Prima di accendere: `ufw default deny incoming`, `ufw default allow outgoing`, **`ufw allow in on tailscale0`** (tutto ciò che arriva dalla rete privata), e **per ora anche `ufw allow 22/tcp`** (rete pubblica) come rete di sicurezza.
2. Accendere UFW. **Prova:** dal PC, SSH via Tailscale funziona; n8n e i servizi locali non cambiano (ascoltano già solo in locale).
3. **Timer di sicurezza:** prima di accendere si programma un `systemd-run --on-active=10m` che spegne UFW da solo se Matteo non lo annulla; si annulla dopo la prova.
4. Più avanti (passo 5), si toglie la riga `22/tcp` pubblica.
**Attenzione:** Docker può aggirare UFW pubblicando le porte. Oggi i contenitori sono pubblicati solo su `127.0.0.1`, quindi non sono esposti; **ogni nuovo contenitore va pubblicato solo su 127.0.0.1**, mai su 0.0.0.0.

## Passo 4 — SSH: niente password, niente accesso diretto di root
1. Salvare una copia di `sshd_config` e dei file in `sshd_config.d/`.
2. Impostare `PasswordAuthentication no`, `PermitRootLogin no` (oppure `prohibit-password` se un servizio automatico entra come root con chiave: da verificare al passo 1), `PubkeyAuthentication yes`, `KbdInteractiveAuthentication no`. Controllare che nessun file in `sshd_config.d/` (per esempio `50-cloud-init.conf`) riporti la password a `yes`.
3. Verificare la sintassi con `sshd -t`, poi ricaricare il servizio **senza chiudere la sessione aperta**.
4. **Prova da una nuova finestra:** con la chiave entra; con la sola password **non** deve entrare; `root` diretto **non** deve entrare.
**Ritorno indietro:** ripristinare la copia di `sshd_config` dalla sessione ancora aperta o dalla console di emergenza.

## Passo 5 — Chiudere SSH pubblico
Quando tutto funziona via Tailscale: togliere `ufw allow 22/tcp` pubblico, lasciando entrare SSH solo da `tailscale0`. **Prova:** da fuori Tailscale (per esempio dalla rete del telefono senza Tailscale) la porta 22 non risponde; dal PC con Tailscale sì. Se Tailscale cade sulla VPS, si rientra dalla console di emergenza.

## Passo 6 — Fail2ban e aggiornamenti automatici
- Installare **fail2ban** per SSH (utile finché la 22 pubblica non è chiusa e come difesa in profondità).
- Attivare gli **aggiornamenti di sicurezza automatici** (`unattended-upgrades`) e un promemoria n8n per i riavvii dopo gli aggiornamenti del kernel.

## Passo 7 — Verifica su Hermes e isolamento (voce 36, solo lettura prima)
- Con quale utente gira Hermes e con quali permessi (può leggere `/root`, i volumi Docker, i dati di n8n e di altri progetti? è nel gruppo `docker`, che equivale a root?).
- Quali porte e cartelle usa; se ha accesso alla rete Tailscale e a quali servizi.
- **Decisione da prendere con Matteo:** (a) dati fiscali sulla stessa macchina in cartelle e database leggibili solo da un utente dedicato, con Hermes tenuto fuori; oppure (b) una **macchina separata** per i dati fiscali (costo minimo, isolamento netto). Se Hermes può agire come root, la (a) non basta.

## Passo 8 — Backup prima di tutto
- Prima di mettere dati reali: backup cifrati giornalieri dei dati fiscali **fuori dalla VPS**, e **una prova di ripristino** su una macchina o cartella di prova.
- Salvare anche la configurazione di n8n e dei flussi (esportazione dei flussi senza credenziali).

## Passo 9 — Chiusura
- Aggiornare `docs/prd-fiscale.md` §10 e le voci 35 e 36 con l'esito; elencare cosa è cambiato sulla macchina (utente, chiavi, regole del firewall, impostazioni SSH) in un file di registro.
- Solo allora si installano Postgres nuovo e Metabase **con dati finti** (voce 30), poi la prova da telefono via Tailscale.

## Che cosa può andare storto e come si rientra
| Rischio | Prevenzione | Rientro |
| --- | --- | --- |
| Si chiude fuori Matteo dopo il cambio di SSH | Chiave provata prima, sessione aperta, timer di ripristino | Console di emergenza del fornitore |
| UFW blocca Tailscale o i servizi | Regola `allow in on tailscale0` prima dell'accensione, timer di spegnimento | Console di emergenza; `ufw disable` |
| `cloud-init` o altro file riporta la password a `yes` | Controllo di `sshd -T` e di `sshd_config.d/` | Correggere il file indicato |
| Un servizio automatico usava la password di root | Controllo al passo 1 prima di spegnere la password | Ripristino della copia di `sshd_config` |
| Un contenitore viene pubblicato su 0.0.0.0 e aggira UFW | Regola: sempre `127.0.0.1:porta` | Rifare il contenitore con la porta corretta |

## Cosa serve da Matteo, in ordine
1. Passo 0 (console di emergenza, nome dell'utente di amministrazione).
2. Un ok per il passo 1 (lettura).
3. Un ok per ogni passo successivo (2, 3, 4, 5, 6): uno alla volta.
4. La decisione del passo 7 (stessa macchina con utente dedicato, oppure macchina separata).
