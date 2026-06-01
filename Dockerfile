FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install PyTorch CPU first (smaller image — GPU available via Railway env)
RUN pip install --no-cache-dir torch==2.3.1 torchaudio==2.3.1 --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir TTS==0.22.0 fastapi==0.115.0 uvicorn[standard]==0.30.6 python-multipart==0.0.9

COPY . .

# Pre-download the model at build time so cold starts are fast
# Comment this out if Railway build times are too long (model = ~2GB)
RUN python -c "from TTS.api import TTS; TTS('eduardem/xtts-v2-romanian')" || true

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
