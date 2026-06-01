# VoxRO — Romanian TTS cu Clonare Vocală

Aplicație web pentru text-to-speech românesc cu clonare vocală, bazată pe modelul [XTTS-v2 fine-tuned Romanian](https://huggingface.co/eduardem/xtts-v2-romanian).

## Funcționalități

- 🎙️ Înregistrare vocală direct în browser sau upload fișier audio
- 🗣️ Clonare vocală + generare TTS în română
- ⚡ 6.3% WER (Whisper large-v3)
- 📱 UI responsive, dark mode

## Deploy pe Railway

### Metoda 1 — GitHub (recomandat)

1. Încarcă acest folder pe GitHub (repo privat sau public)
2. Mergi pe [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**
3. Selectează repo-ul tău
4. Railway detectează automat `Dockerfile` și `railway.toml`
5. Dă click **Deploy** — gata!

### Metoda 2 — Railway CLI

```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

## Setări Railway recomandate

| Setare | Valoare |
|--------|---------|
| Plan | **Hobby** sau **Pro** (modelul e ~2GB RAM) |
| RAM | minim **4GB** recomandat |
| CPU | 2+ cores |
| Storage | modelul se descarcă la build (~2GB) |

> **Notă**: Modelul XTTS-v2 Romanian se descarcă automat de pe HuggingFace la prima pornire (sau la build dacă linia din Dockerfile nu e comentată). Primul start poate dura 2–5 minute.

## Structura proiectului

```
.
├── app.py              # FastAPI backend
├── static/
│   └── index.html      # Frontend UI
├── requirements.txt
├── Dockerfile
└── railway.toml
```

## Dezvoltare locală

```bash
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
# Deschide http://localhost:8000
```

## Limite

- Text max: 2000 caractere per request
- Format audio suportat: WAV, MP3, FLAC, OGG
- Mostră vocală minimă recomandată: 6 secunde
- Generarea durează ~5–30 sec în funcție de lungimea textului și hardware
