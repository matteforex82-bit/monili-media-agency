# Configura il PC per usare lo Studio dal telefono ovunque, con Tailscale.
# Si lancia una volta sola con "Configura Telefono.bat": chiede i permessi di amministratore,
# installa Tailscale, tiene il PC sveglio sotto corrente e apre le porte solo alla rete Tailscale.

$ErrorActionPreference = "Stop"

$principal = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Start-Process powershell -Verb RunAs -ArgumentList "-NoProfile", "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "`"$PSCommandPath`""
    exit
}

function Step($text) {
    Write-Host ""
    Write-Host "==> $text" -ForegroundColor Cyan
}

$TailscaleExe = "$env:ProgramFiles\Tailscale\tailscale.exe"

Step "1/4 Installo Tailscale"
if (Test-Path $TailscaleExe) {
    Write-Host "Gia installato."
} elseif (Get-Command winget -ErrorAction SilentlyContinue) {
    winget install --id Tailscale.Tailscale -e --silent --accept-source-agreements --accept-package-agreements
    Start-Sleep -Seconds 5
} else {
    Write-Host "winget non disponibile: installa Tailscale da https://tailscale.com/download/windows e rilancia questo file." -ForegroundColor Yellow
    exit 1
}
if (-not (Test-Path $TailscaleExe)) {
    Write-Host "Installazione non riuscita: installa Tailscale da https://tailscale.com/download/windows e rilancia." -ForegroundColor Yellow
    exit 1
}

Step "2/4 Accesso a Tailscale"
$TailscaleIp = (& $TailscaleExe ip -4 2>$null | Select-Object -First 1)
if (-not $TailscaleIp) {
    Write-Host "Si apre il browser: accedi (per esempio con Google). Sull'iPhone userai lo STESSO account."
    & $TailscaleExe up
    $TailscaleIp = (& $TailscaleExe ip -4 2>$null | Select-Object -First 1)
}
if ($TailscaleIp) {
    Write-Host "Collegato: $TailscaleIp"
} else {
    Write-Host "Accesso non completato: apri Tailscale dalle icone in basso a destra, fai Log in e rilancia." -ForegroundColor Yellow
}

Step "3/4 PC sempre sveglio quando e collegato alla corrente"
powercfg /change standby-timeout-ac 0
powercfg /change hibernate-timeout-ac 0
Write-Host "Fatto (lo schermo puo comunque spegnersi; a batteria non cambia niente)."

Step "4/4 Porte 3000 e 8000 aperte solo ai dispositivi Tailscale"
if (Get-NetFirewallRule -DisplayName "Monili via Tailscale" -ErrorAction SilentlyContinue) {
    Write-Host "Regola gia presente."
} else {
    New-NetFirewallRule -DisplayName "Monili via Tailscale" -Direction Inbound -Protocol TCP -LocalPort 3000,8000 -RemoteAddress 100.64.0.0/10 -Action Allow | Out-Null
    Write-Host "Regola creata."
}

Write-Host ""
Write-Host "PC pronto." -ForegroundColor Green
Write-Host "Sull'iPhone: installa l'app Tailscale dall'App Store e accedi con lo stesso account."
Write-Host "Poi avvia lo Studio come sempre e apri sull'iPhone:"
if ($TailscaleIp) {
    Write-Host "    http://${TailscaleIp}:3000" -ForegroundColor Green
} else {
    Write-Host "    l'indirizzo 'iPhone (ovunque, Tailscale)' che stampa scripts\start-local.ps1"
}
Write-Host "In Safari: Condividi -> Aggiungi alla schermata Home."
