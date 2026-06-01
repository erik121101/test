import os
import uuid
import json
import threading
from pathlib import Path
from flask import Flask, request, jsonify, send_file, render_template, send_from_directory

app = Flask(__name__)

UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

jobs = {}
jobs_lock = threading.Lock()

def get_model():
    import torch
    from omnivoice import OmniVoice
    if not hasattr(get_model, "_model"):
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        print(f"Loading OmniVoice on {device}...")
        get_model._model = OmniVoice.from_pretrained(
            "k2-fsa/OmniVoice",
            device_map=device,
            dtype=dtype,
        )
        print("Model loaded.")
    return get_model._model

def run_tts(job_id, text, ref_audio_path, ref_text, output_path):
    try:
        import soundfile as sf
        with jobs_lock:
            jobs[job_id]["status"] = "running"
        model = get_model()
        kwargs = {"text": text}
        if ref_audio_path:
            kwargs["ref_audio"] = str(ref_audio_path)
            if ref_text:
                kwargs["ref_text"] = ref_text
        audio = model.generate(**kwargs)
        sf.write(str(output_path), audio[0], 24000)
        with jobs_lock:
            jobs[job_id]["status"] = "done"
            jobs[job_id]["output"] = str(output_path)
    except Exception as e:
        with jobs_lock:
            jobs[job_id]["status"] = "error"
            jobs[job_id]["error"] = str(e)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/synthesize", methods=["POST"])
def synthesize():
    text = request.form.get("text", "").strip()
    if not text:
        return jsonify({"error": "Text is required"}), 400

    ref_audio_path = None
    ref_text = request.form.get("ref_text", "").strip()

    if "ref_audio" in request.files and request.files["ref_audio"].filename:
        f = request.files["ref_audio"]
        ext = Path(f.filename).suffix or ".wav"
        ref_audio_path = UPLOAD_DIR / f"{uuid.uuid4()}{ext}"
        f.save(ref_audio_path)
    elif request.form.get("voice_id"):
        voice_id = request.form.get("voice_id")
        candidate = UPLOAD_DIR / f"{voice_id}.wav"
        if candidate.exists():
            ref_audio_path = candidate
            saved_ref = UPLOAD_DIR / f"{voice_id}.txt"
            if saved_ref.exists() and not ref_text:
                ref_text = saved_ref.read_text().strip()

    job_id = str(uuid.uuid4())
    output_path = OUTPUT_DIR / f"{job_id}.wav"

    with jobs_lock:
        jobs[job_id] = {"status": "queued"}

    t = threading.Thread(target=run_tts, args=(job_id, text, ref_audio_path, ref_text, output_path), daemon=True)
    t.start()

    return jsonify({"job_id": job_id})

@app.route("/api/job/<job_id>")
def job_status(job_id):
    with jobs_lock:
        job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Not found"}), 404
    return jsonify(job)

@app.route("/api/audio/<job_id>")
def get_audio(job_id):
    with jobs_lock:
        job = jobs.get(job_id)
    if not job or job.get("status") != "done":
        return jsonify({"error": "Not ready"}), 404
    return send_file(job["output"], mimetype="audio/wav", as_attachment=False)

@app.route("/api/clone-voice", methods=["POST"])
def clone_voice():
    if "audio" not in request.files or not request.files["audio"].filename:
        return jsonify({"error": "No audio file provided"}), 400
    f = request.files["audio"]
    voice_name = request.form.get("name", "").strip() or str(uuid.uuid4())[:8]
    voice_id = voice_name.lower().replace(" ", "_")
    ext = Path(f.filename).suffix or ".wav"
    dest = UPLOAD_DIR / f"{voice_id}{ext}"
    f.save(dest)
    ref_text = request.form.get("ref_text", "").strip()
    if ref_text:
        (UPLOAD_DIR / f"{voice_id}.txt").write_text(ref_text)
    voices = load_voices()
    voices[voice_id] = {"name": voice_name, "file": str(dest)}
    save_voices(voices)
    return jsonify({"voice_id": voice_id, "name": voice_name})

@app.route("/api/voices")
def list_voices():
    return jsonify(load_voices())

VOICES_FILE = Path("voices.json")

def load_voices():
    if VOICES_FILE.exists():
        return json.loads(VOICES_FILE.read_text())
    return {}

def save_voices(data):
    VOICES_FILE.write_text(json.dumps(data, indent=2))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
