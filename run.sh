#!/usr/bin/env bash
# Ghostlight — light the whole altar with one command.
#
#   1. Downloads llama.cpp (first run only) and the Gemma 3 1B open weights.
#   2. Starts llama-server with Gemma on http://127.0.0.1:8080
#   3. Starts the Ghostlight app on http://localhost:8000
#
# Everything runs locally. No cloud API is ever called.

set -euo pipefail
cd "$(dirname "$0")"

LLAMA_TAG="b12023"
VENDOR="vendor"
MODEL_DIR="models"
MODEL_FILE="gemma-3-1b-it-Q4_K_M.gguf"
MODEL_URL="https://huggingface.co/ggml-org/gemma-3-1b-it-GGUF/resolve/main/${MODEL_FILE}"

mkdir -p "$VENDOR" "$MODEL_DIR"

if [ ! -x "$VENDOR/llama-b${LLAMA_TAG# b}/llama-server" ] && ! ls "$VENDOR"/*/llama-server >/dev/null 2>&1; then
  echo "==> Downloading llama.cpp (${LLAMA_TAG}, CPU build)…"
  curl -sL -o "$VENDOR/llama.tar.gz" \
    "https://github.com/ggml-org/llama.cpp/releases/download/${LLAMA_TAG}/llama-${LLAMA_TAG}-bin-ubuntu-x64.tar.gz"
  tar --no-same-owner -xzf "$VENDOR/llama.tar.gz" -C "$VENDOR"
fi
LLAMA_SERVER="$(ls "$VENDOR"/*/llama-server | head -1)"
echo "==> llama.cpp: $LLAMA_SERVER"

if [ ! -f "$MODEL_DIR/$MODEL_FILE" ]; then
  echo "==> Downloading Gemma 3 1B (open weights, ~0.8 GB, one time)…"
  curl -L -o "$MODEL_DIR/$MODEL_FILE" "$MODEL_URL"
fi

echo "==> Starting Gemma on http://127.0.0.1:8080 …"
"$LLAMA_SERVER" -m "$MODEL_DIR/$MODEL_FILE" --host 127.0.0.1 --port 8080 \
  -c 4096 --jinja > models-server.log 2>&1 &
LLAMA_PID=$!
trap 'kill $LLAMA_PID 2>/dev/null || true' EXIT

for i in $(seq 1 60); do
  if curl -s http://127.0.0.1:8080/health >/dev/null 2>&1; then break; fi
  sleep 1
done

echo "==> Ghostlight is lit: http://localhost:8000"
python3 app.py
