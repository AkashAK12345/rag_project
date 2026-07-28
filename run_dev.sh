#!/bin/bash
# run_dev.sh
# Starts the FastAPI backend in development mode with auto-reloading enabled.
# We explicitly exclude runtime-generated directories (uploads, storage, metadata) 
# to prevent the server from restarting every time the indexing service writes files.

uvicorn api_main:app \
  --reload \
  --reload-exclude "uploads" \
  --reload-exclude "storage" \
  --reload-exclude "metadata" \
  --reload-exclude "*.db" \
  --reload-exclude "__pycache__"
