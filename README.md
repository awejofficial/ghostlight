# 🕯️ Ghostlight — a local-AI ofrenda

**A digital altar for Día de los Muertos, lit by a ghost that lives on your own machine.**

*Submission for the [Hacktoberfest Open-Source AI Challenge Week 4: Ghost in the Machine](https://dev.to/challenges/hacktoberfest-week4-2026-10-26) · Prize category entered: **Best Use of Gemma***

---

## The idea

On Día de los Muertos (Nov 1–2), families in Mexico build an **ofrenda** — an altar with photos, candles, marigolds (*cempasúchil*), and the departed's favourite food — so the people they lost can find their way back for one evening.

Ghostlight is that altar, as software. You leave:

- a **name**,
- who they were to you,
- an **offering** (their favourite food),
- a **song** that brings them back, and
- one **memory**.

Then **Gemma 3** — Google's open-weight model, running **100% locally** via [llama.cpp](https://github.com/ggml-org/llama.cpp) — does the one thing a static webpage can't: it finds the words.

- **Remembrance mode** — the keeper of the altar writes a short, warm remembrance.
- **Séance mode** — the ghost in the machine answers back: a short first-person message, as if they noticed the candle and spoke one last time.

Every altar you light is saved in a local JSON file on *your* disk, so the altar is still there next year. Delete the file and it's gone — the dead keep no backups.

## Why it had to be open

A remembrance is one of the most private texts a person will ever write. It should never be typed into a cloud API, logged on someone else's server, or held hostage by a subscription. Because Gemma's weights are open and llama.cpp is open source, Ghostlight:

- works **offline**, on an ordinary laptop, with the Wi-Fi off;
- sends **nothing** anywhere — the memories stay on the machine that made them;
- costs **nothing** to run, forever;
- can swap models with one command-line flag (the ghost can change its voice);
- will still work the year the hosted demo dies — fitting, for a project about things that disappear.

## Tech

| Piece | What it is |
|---|---|
| Model | **Gemma 3 1B Instruct** (open weights), `Q4_K_M` GGUF (~0.8 GB) |
| Inference | **llama.cpp** `llama-server`, OpenAI-compatible API on `127.0.0.1:8080` |
| App | Python 3 standard library only — `http.server`, **zero pip installs** |
| Front end | Vanilla HTML/CSS/JS — candle-flicker flames, falling marigold petals, typewriter reveal |
| Storage | One local JSON file (`data/altars.json`) |

## Run it

You need Python 3 and `curl`. That's all.

```bash
git clone https://github.com/awejofficial/ghostlight.git
cd ghostlight
bash run.sh
```

First run downloads llama.cpp and the Gemma weights (~0.85 GB total) into folders that are git-ignored. Then open:

**http://localhost:8000**

Already have llama.cpp / Ollama-style serving running? Just start `python3 app.py` with any OpenAI-compatible server on `:8080` (set `LLAMA_BASE` to change the endpoint).

## Sample output (real, from Gemma 3 1B on a laptop CPU)

Lit for "Aaji" — grandmother, puran poli and warm milk as the offering, an abhang as
the song, evenings counting first stars on a terrace in Phaltan as the memory.
Verbatim model output, generated locally, offline:

> The air smells of marigolds, a slow, fragrant offering to you. Aaji's presence here
> feels like the twilight deepening, a gentle hush settling over the space. You've
> lit a small flame, a single point of warmth in this quiet moment.
>
> I remember your hands, steady and sure, tracing the patterns of the evening sky…
> Puran poli, warm and comforting, nestled beside the milk, a symbol of her love.
>
> You hummed an old abhang song, a melody of longing and resilience, while rolling
> rotis. I recall evenings spent on the terrace in Phaltan, your watchful gaze fixed
> on the first stars, each one a silent, watchful guardian.
>
> Now, as the candles burn, you are with us again, a warmth that lingers in the quiet.

## Honest notes

- A 1B model writes like a thoughtful friend, not a poet laureate. Occasionally it is generic; the keeper's prompt (specific food, a specific memory) is what makes it personal. A bigger Gemma (4B/12B) drops in with one flag if your machine can carry it.
- Ghostlight is a remembrance toy, not a grief counsellor. It keeps memories; it doesn't replace people.

## Licence

MIT. The marigolds are everyone's.
