#!/bin/bash

# Avvia Ollama in background
ollama serve &

# Attendi finché Ollama non è pronto
until curl -s http://localhost:11434 > /dev/null; do
    echo "Aspettando Ollama..."
    sleep 2
done
echo "Ollama è pronto!"

# Avvia FastAPI con Uvicorn
exec uvicorn main:app --host 0.0.0.0 --port 8000
