@echo off
title Servidor Movil - Beyker
color 0A
cls
echo ==============================================================
echo           INICIANDO BEYKER PARA TU CELULAR Y PC
echo ==============================================================
echo.
cd /d "%~dp0\mobile_app"
python server.py
pause
