#!/bin/bash
# Controllo della VPS in SOLA LETTURA per il back-office fiscale (docs/prd-fiscale.md, voce 30).
# Non modifica, non installa, non legge variabili d'ambiente, password, chiavi o dati dei flussi.
# Mostra: sistema, risorse, container attivi (nome, immagine, porte), porte in ascolto,
# firewall, servizi noti, impostazioni SSH principali.

echo "== SISTEMA"
. /etc/os-release 2>/dev/null; echo "${PRETTY_NAME:-sconosciuto}"; uname -r; uptime -p
echo "== RISORSE"
free -h | head -2; df -h / | tail -1; echo "cpu: $(nproc)"
echo "== DOCKER"
if command -v docker >/dev/null 2>&1; then
  docker ps --format "{{.Names}} | {{.Image}} | {{.Ports}} | {{.Status}}"
else
  echo "docker non presente"
fi
echo "== PORTE IN ASCOLTO"
ss -tlnp 2>/dev/null | awk 'NR==1 || /LISTEN/ {print $4, $6}' | sed 's/users:(("//; s/",pid.*//' | head -40
echo "== FIREWALL"
if command -v ufw >/dev/null 2>&1; then ufw status | head -15; else echo "ufw assente"; fi
echo "== TAILSCALE"
tailscale status 2>/dev/null | head -6
echo "== SERVIZI NOTI"
for s in postgresql nginx caddy fail2ban cron; do
  # is-active stampa già lo stato (active/inactive/unknown): niente "|| echo" che lo confonderebbe
  printf "%s: " "$s"; systemctl is-active "$s" 2>/dev/null || true
done
echo "(n8n e Postgres possono girare in Docker o con unità dal nome diverso: vedi DOCKER e PORTE)"
echo "== SSH (impostazioni principali)"
grep -Ei '^(PermitRootLogin|PasswordAuthentication|PubkeyAuthentication)' /etc/ssh/sshd_config 2>/dev/null
echo "== FINE"
