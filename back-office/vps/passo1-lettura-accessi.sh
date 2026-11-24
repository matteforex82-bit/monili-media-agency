#!/bin/bash
# Passo 1 del piano docs/piano-sicurezza-vps.md: stato degli ACCESSI, in SOLA LETTURA.
# Non modifica nulla. Non stampa chiavi, password, variabili d'ambiente né argomenti dei processi.

echo "== SSH: IMPOSTAZIONI EFFETTIVE"
sshd -T 2>/dev/null | grep -Ei '^(permitrootlogin|passwordauthentication|pubkeyauthentication|kbdinteractiveauthentication|challengeresponseauthentication|usepam|port|listenaddress|allowusers|allowgroups|maxauthtries)'
echo "== SSH: FILE CHE POSSONO FORZARE LE IMPOSTAZIONI"
ls -1 /etc/ssh/sshd_config.d/ 2>/dev/null
grep -HEi '^(PasswordAuthentication|PermitRootLogin)' /etc/ssh/sshd_config.d/*.conf 2>/dev/null
echo "== CHIAVI AUTORIZZATE (solo impronte e commento)"
for f in /root/.ssh/authorized_keys /home/*/.ssh/authorized_keys; do
  [ -f "$f" ] || continue
  echo "-- $f"
  ssh-keygen -lf "$f" 2>/dev/null | awk '{print $1, $2, $NF}'
done
echo "== UTENTI CON SHELL DI ACCESSO"
awk -F: '$7 !~ /(nologin|false)$/ {print $1, "uid="$3, $7}' /etc/passwd
echo "== GRUPPI CHE EQUIVALGONO A ROOT (sudo, docker)"
getent group sudo docker
echo "== ACCESSI RECENTI (ultimi 12, senza dettagli sensibili)"
last -n 12 -a 2>/dev/null | awk '{print $1, $3, $4, $5, $6, $7}' | head -14
echo "== TENTATIVI FALLITI OGGI (conteggio)"
journalctl -u ssh --since today 2>/dev/null | grep -c "Failed password"
echo "== HERMES: SERVIZI E UTENTE (nessun argomento, nessuna variabile)"
systemctl list-units --type=service --all 2>/dev/null | grep -i hermes | awk '{print $1, $3, $4}'
ps -eo user,pid,comm 2>/dev/null | grep -i hermes
echo "== FIREWALL"
ufw status 2>/dev/null | head -5
echo "== FINE"
