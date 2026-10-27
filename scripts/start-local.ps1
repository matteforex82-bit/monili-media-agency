param(
    [string]$StorageDir = "$env:USERPROFILE\MoniliStorage",
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 3000
)

$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$Frontend = Join-Path $Root "frontend"
$LocalIp = (
    Get-NetIPConfiguration |
    Where-Object { $_.IPv4DefaultGateway -and $_.IPv4Address } |
    ForEach-Object { $_.IPv4Address.IPAddress } |
    Where-Object { $_ -and $_ -notlike "169.254.*" -and $_ -ne "127.0.0.1" } |
    Select-Object -First 1
)
if (-not $LocalIp) {
    $LocalIp = "localhost"
}
# Indirizzo Tailscale (100.x.y.z): per usare l'app dal telefono anche fuori dal Wi-Fi
$TailscaleIp = $null
$TailscaleCli = Get-Command tailscale -ErrorAction SilentlyContinue
if (-not $TailscaleCli -and (Test-Path "$env:ProgramFiles\Tailscale\tailscale.exe")) {
    $TailscaleCli = Get-Command "$env:ProgramFiles\Tailscale\tailscale.exe"
}
if ($TailscaleCli) {
    $TailscaleIp = (& $TailscaleCli.Source ip -4 2>$null | Select-Object -First 1)
}

New-Item -ItemType Directory -Force -Path $StorageDir | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $StorageDir "input") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $StorageDir "output") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $StorageDir "memory") | Out-Null

$env:MONILI_STORAGE_DIR = $StorageDir
# Il frontend chiama il backend sullo stesso indirizzo con cui apri la pagina (vedi frontend/src/lib/apiUrl.ts)
$env:NEXT_PUBLIC_API_PORT = "$BackendPort"

Write-Host ""
Write-Host "Monili locale"
Write-Host "Storage:  $StorageDir"
Write-Host "Backend:  http://localhost:$BackendPort"
Write-Host "Frontend: http://localhost:$FrontendPort"
Write-Host "iPhone (stesso Wi-Fi):   http://${LocalIp}:$FrontendPort"
if ($TailscaleIp) {
    Write-Host "iPhone (ovunque, Tailscale): http://${TailscaleIp}:$FrontendPort"
} else {
    Write-Host "Tailscale non trovato: fuori dal Wi-Fi l'app non si raggiunge (guida in docs/local-mode.md)"
}
Write-Host ""
Write-Host "Il PC deve restare acceso e non andare in sospensione."
Write-Host "Lascia aperte entrambe le finestre PowerShell che si aprono."
Write-Host ""

$backendCommand = "`$env:MONILI_STORAGE_DIR='$StorageDir'; cd '$Root'; python -m pip install -q -r requirements.txt; python -m uvicorn api.server:app --host 0.0.0.0 --port $BackendPort"
$frontendCommand = "`$env:NEXT_PUBLIC_API_PORT='$BackendPort'; cd '$Frontend'; npm run dev:local"

Start-Process powershell -WindowStyle Normal -ArgumentList "-NoExit", "-Command", $backendCommand
Start-Sleep -Seconds 2
Start-Process powershell -WindowStyle Normal -ArgumentList "-NoExit", "-Command", $frontendCommand
