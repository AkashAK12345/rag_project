@echo off
REM run_dev.bat
REM Starts the FastAPI backend in development mode with auto-reloading enabled.
REM We explicitly exclude runtime-generated directories (uploads, storage, metadata) 
REM to prevent the server from restarting every time the indexing service writes files.

uvicorn api_main:app ^
  --reload ^
  --reload-exclude "uploads" ^
  --reload-exclude "storage" ^
  --reload-exclude "metadata" ^
  --reload-exclude "*.db" ^
  --reload-exclude "__pycache__"
