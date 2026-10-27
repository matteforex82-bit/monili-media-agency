@echo off
rem Configura il PC per usare lo Studio dal telefono ovunque (Tailscale). Da lanciare una volta sola.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\setup-telefono.ps1"
