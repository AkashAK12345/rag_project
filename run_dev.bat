@echo off
REM run_dev.bat
REM Starts the FastAPI backend in development mode with auto-reloading enabled.
REM We explicitly whitelist python directories to prevent runtime files (logs/storage) from triggering infinite reloads.

uvicorn api_main:app --host 0.0.0.0 --port 8000 --reload --reload-dir api --reload-dir services --reload-dir schemas --reload-dir core --reload-dir models --reload-dir analytics --reload-dir forecasting --reload-dir reports --reload-dir indexing --reload-dir loaders --reload-dir sources --reload-dir connectors --reload-dir repositories --reload-dir tools --reload-dir config
