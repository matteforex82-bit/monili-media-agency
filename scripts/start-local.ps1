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
$ApiUrl = "http://${LocalIp}:$BackendPort"

New-Item -ItemType Directory -Force -Path $StorageDir | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $StorageDir "input") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $StorageDir "output") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $StorageDir "memory") | Out-Null

$env:MONILI_STORAGE_DIR = $StorageDir
$env:NEXT_PUBLIC_API_URL = $ApiUrl

Write-Host ""
Write-Host "Monili locale"
Write-Host "Storage:  $StorageDir"
Write-Host "Backend:  http://localhost:$BackendPort"
Write-Host "Frontend: http://localhost:$FrontendPort"
Write-Host "iPhone:   http://${LocalIp}:$FrontendPort"
Write-Host "API URL:  $ApiUrl"
Write-Host ""
Write-Host "Per iPhone: apri l'URL iPhone qui sopra sulla stessa rete Wi-Fi."
Write-Host "Lascia aperte entrambe le finestre PowerShell che si aprono."
Write-Host ""

$backendCommand = "`$env:MONILI_STORAGE_DIR='$StorageDir'; cd '$Root'; python -m uvicorn api.server:app --host 0.0.0.0 --port $BackendPort"
$frontendCommand = "`$env:NEXT_PUBLIC_API_URL='$ApiUrl'; cd '$Frontend'; npm run dev:local"

Start-Process powershell -WindowStyle Normal -ArgumentList "-NoExit", "-Command", $backendCommand
Start-Sleep -Seconds 2
Start-Process powershell -WindowStyle Normal -ArgumentList "-NoExit", "-Command", $frontendCommand
