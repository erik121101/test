FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Accept Coqui TTS license non-interactively
ENV COQUI_TOS_AGREED=1

# Install PyTorch CPU
RUN pip install --no-cache-dir torch==2.3.1 torchaudio==2.3.1 --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir TTS==0.22.0 fastapi==0.115.0 uvicorn[standard]==0.30.6 python-multipart==0.0.9

COPY . .

# Pre-download model at build time (COQUI_TOS_AGREED=1 e setat, nu mai cere interactiv)
RUN python -c "from TTS.api import TTS; TTS('eduardem/xtts-v2-romanian')"

EXPOSE 8000

CMD uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}
