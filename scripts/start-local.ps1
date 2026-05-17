param(
    [string]$StorageDir = "$env:USERPROFILE\MoniliStorage",
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 3000
)

$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$Frontend = Join-Path $Root "frontend"

New-Item -ItemType Directory -Force -Path $StorageDir | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $StorageDir "input") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $StorageDir "output") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $StorageDir "memory") | Out-Null

$env:MONILI_STORAGE_DIR = $StorageDir
$env:NEXT_PUBLIC_API_URL = "http://localhost:$BackendPort"

Write-Host ""
Write-Host "Monili locale"
Write-Host "Storage:  $StorageDir"
Write-Host "Backend:  http://localhost:$BackendPort"
Write-Host "Frontend: http://localhost:$FrontendPort"
Write-Host ""
Write-Host "Per iPhone: apri l'indirizzo IP del portatile sulla stessa rete, es. http://192.168.1.20:$FrontendPort"
Write-Host "Lascia aperte entrambe le finestre PowerShell che si aprono."
Write-Host ""

$backendCommand = "`$env:MONILI_STORAGE_DIR='$StorageDir'; cd '$Root'; python -m uvicorn api.server:app --host 0.0.0.0 --port $BackendPort"
$frontendCommand = "`$env:NEXT_PUBLIC_API_URL='http://localhost:$BackendPort'; cd '$Frontend'; npm run dev:local"

Start-Process powershell -WindowStyle Normal -ArgumentList "-NoExit", "-Command", $backendCommand
Start-Sleep -Seconds 2
Start-Process powershell -WindowStyle Normal -ArgumentList "-NoExit", "-Command", $frontendCommand
