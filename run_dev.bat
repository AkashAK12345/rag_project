@echo off
REM run_dev.bat
REM Starts the FastAPI backend in development mode with auto-reloading enabled.
REM We explicitly exclude runtime-generated directories (uploads, storage, metadata) 
REM to prevent the server from restarting every time the indexing service writes files.

python api_main.py --dev
