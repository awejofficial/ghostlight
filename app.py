#!/usr/bin/env python3
"""
Ghostlight — a local-AI ofrenda for Dia de los Muertos.

A private, offline digital altar. You leave a name, a favourite food, a song
and a memory; Gemma 3 (Google's open-weight model), running 100% locally via
llama.cpp, writes a short remembrance — or, in seance mode, a short message
written as if the departed were speaking back.

Grief is private. Nothing you type here ever leaves your machine:
there is no cloud API, no account, no analytics. The model is a file on
your disk and the altars you light are stored in a local JSON file.

Run:
    ./run.sh            # starts llama-server (Gemma) + this app
    # or, with llama-server already running:
    python3 app.py      # http://localhost:8000
"""

import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(ROOT, "static")
DATA_DIR = os.path.join(ROOT, "data")
ALTARS_FILE = os.path.join(DATA_DIR, "altars.json")

LLAMA_BASE = os.environ.get("LLAMA_BASE", "http://127.0.0.1:8080")
APP_PORT = int(os.environ.get("PORT", "8000"))

SYSTEM_PROMPT = (
    "You are the keeper of a small Dia de los Muertos ofrenda (altar of remembrance). "
    "Your voice is warm, gentle and poetic, never cheesy and never frightening. "
    "You write only the remembrance itself, with no preamble, no quotation marks "
    "and no explanation."
)

def build_user_prompt(fields):
    name = fields["name"]
    relation = fields.get("relation") or "someone beloved"
    food = fields.get("food") or ""
    song = fields.get("song") or ""
    memory = fields.get("memory") or ""
    mode = fields.get("mode") or "remembrance"

    details = [f"Name of the departed: {name}", f"Who they were: {relation}"]
    if food:
        details.append(f"Their favourite food, left on the altar as an offering: {food}")
    if song:
        details.append(f"A song that brings them back: {song}")
    if memory:
        details.append(f"A memory the keeper shared: {memory}")
    detail_block = "\n".join(details)

    if mode == "seance":
        return (
            f"{detail_block}\n\n"
            f"Write a short message (70-110 words) in the FIRST PERSON, as if {name} "
            "is speaking one last time to the person who lit this candle. Weave in the "
            "offering and the memory naturally, as things they notice and smile about. "
            "Be comforting, specific and full of love, the way a voice from a happy "
            "memory would sound. End by signing off with just their name."
        )
    return (
        f"{detail_block}\n\n"
        f"Write a short remembrance (90-130 words) for {name}, addressed warmly to "
        "the person who lit this candle. Weave in the offering and the memory "
        "naturally. Make it feel like the moment a candle is lit on the ofrenda: "
        "the marigolds are out, the photo is placed, and for one evening they are "
        "with us again. End with a single quiet line about the candle staying lit."
    )

def call_model(fields):
    payload = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(fields)},
        ],
        "max_tokens": 240,
        "temperature": 0.85,
        "top_p": 0.95,
    }
    req = urllib.request.Request(
        f"{LLAMA_BASE}/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    text = data["choices"][0]["message"]["content"].strip()
    # Small models sometimes add wrapping quotes; keep the altar clean.
    if len(text) > 1 and text[0] == '"' and text[-1] == '"':
        text = text[1:-1].strip()
    return text

def model_alive():
    try:
        req = urllib.request.Request(f"{LLAMA_BASE}/health", method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status == 200
    except Exception:
        return False

def load_altars():
    if not os.path.exists(ALTARS_FILE):
        return []
    try:
        with open(ALTARS_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return []

def save_altar(record):
    os.makedirs(DATA_DIR, exist_ok=True)
    altars = load_altars()
    altars.insert(0, record)
    with open(ALTARS_FILE, "w", encoding="utf-8") as fh:
        json.dump(altars, fh, ensure_ascii=False, indent=2)

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # keep the terminal quiet, like a chapel
        pass

    def _json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _file(self, path, content_type):
        try:
            with open(path, "rb") as fh:
                body = fh.read()
        except OSError:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._file(os.path.join(STATIC_DIR, "index.html"), "text/html; charset=utf-8")
        elif self.path == "/styles.css":
            self._file(os.path.join(STATIC_DIR, "styles.css"), "text/css; charset=utf-8")
        elif self.path == "/app.js":
            self._file(os.path.join(STATIC_DIR, "app.js"), "text/javascript; charset=utf-8")
        elif self.path == "/api/health":
            self._json({"app": "ok", "model": "ok" if model_alive() else "down"})
        elif self.path == "/api/altars":
            self._json({"altars": load_altars()})
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path != "/api/light":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            fields = json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            self._json({"error": "That request did not arrive intact. Try again."}, 400)
            return

        name = (fields.get("name") or "").strip()
        if not name:
            self._json({"error": "An altar needs a name. Whose candle is this?"}, 400)
            return
        clean = {
            "name": name[:80],
            "relation": (fields.get("relation") or "").strip()[:120],
            "food": (fields.get("food") or "").strip()[:120],
            "song": (fields.get("song") or "").strip()[:120],
            "memory": (fields.get("memory") or "").strip()[:1200],
            "mode": "seance" if fields.get("mode") == "seance" else "remembrance",
        }

        if not model_alive():
            self._json(
                {
                    "error": "The ghost is silent: the local model is not running. "
                    "Start it with ./run.sh (llama.cpp + Gemma) and light the candle again."
                },
                503,
            )
            return

        try:
            words = call_model(clean)
        except Exception:
            self._json(
                {"error": "The candle flickered and went out (the model call failed). Try once more."},
                502,
            )
            return

        record = {
            **clean,
            "words": words,
            "lit_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        save_altar(record)
        self._json({"altar": record})

if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", APP_PORT), Handler)
    print(f"Ghostlight is lit at http://localhost:{APP_PORT}")
    print(f"Talking to the ghost at {LLAMA_BASE} (Gemma via llama.cpp)")
    server.serve_forever()
