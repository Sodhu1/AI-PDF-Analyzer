# Usa un'immagine base di Python
FROM python:3

# Imposta la directory di lavoro all'interno del container
WORKDIR /app

EXPOSE 8000/tcp

# Copia il file di requisiti nel container
COPY requirements.txt .

# Scarica ollama e altre dipendenze
RUN apt-get update && \
    apt-get install -y curl ghostscript libgs-dev uvicorn && \
    curl -sSL https://ollama.com/install.sh | bash

RUN ollama serve & sleep 5 && ollama pull phi4:14b

# Installa le dipendenze
RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice sorgente dell'applicazione
COPY . .

RUN chmod +x /app/start.sh

# Esegui script di avvio
CMD ["/app/start.sh"]
