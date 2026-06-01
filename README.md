# OmniVoice TTS Web App

Voice cloning & text-to-speech web app powered by [OmniVoice](https://github.com/k2-fsa/OmniVoice).

## Features
- Upload a short voice clip to clone a voice
- Save multiple named voices
- Generate speech in 600+ languages using cloned or auto voice
- Clean dark-mode UI

## Deploy on Railway

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
gh repo create omnivoice-tts --public --push
```

### 2. Deploy on Railway
1. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
2. Select your repo
3. Railway auto-detects the config from `railway.toml` and `nixpacks.toml`
4. **Important**: In Railway settings, set the instance to have **at least 4GB RAM** (model is ~2GB)
5. If you have a GPU instance, inference will be much faster

### Environment variables (optional)
| Variable | Default | Description |
|---|---|---|
| `PORT` | 8080 | Auto-set by Railway |
| `HF_ENDPOINT` | — | Set to `https://hf-mirror.com` if HuggingFace is slow |

### Notes
- First start takes ~2–3 min to download the OmniVoice model from HuggingFace (~2GB)
- Railway's free tier has a 512MB RAM limit — **you need a paid plan** for this app
- Recommended: Railway Hobby plan + at least 4GB RAM in instance settings
- Without GPU, generation takes ~5–15 sec depending on text length

## Local development
```bash
pip install -r requirements.txt
python app.py
```
Open http://localhost:8080
