@echo off
echo ========================================
echo AION WhatsApp Bot - Envio Automatico
echo ========================================
echo.
echo 1. Escaneie o QR Code com WhatsApp
echo 2. O bot enviara automaticamente
echo 3. Delay de 15s entre mensagens
echo.
cd /d "%~dp0"
node send.js
pause
