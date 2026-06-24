@echo off
color 0A
echo ==========================================
echo        Local AI Workstation Updater
echo ==========================================
echo.
echo [1/2] Updating AI Brains (Ollama)...
ollama pull qwen2.5-coder:latest
ollama pull deepseek-r1:latest
echo.
echo [2/2] Updating Chat Interface (LibreChat)...
wsl -d RajS23-Hanji -e bash -c "cd ~/LibreChat && sudo docker compose pull && sudo docker compose up -d"
echo.
echo ==========================================
echo    ALL SYSTEMS UPDATED AND ONLINE!
echo ==========================================
pause