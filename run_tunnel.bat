@echo off
SETLOCAL
REM Path to Cloudflared
set "CLOUDFLARE=tools\cloudflared-windows.exe"

REM REM: Run cloudflared temporary tunnel localhost:5000
echo Starting Cloudflared tunnel on http://localhost:5000 ...
"%CLOUDFLARE%" tunnel --url http://localhost:5000