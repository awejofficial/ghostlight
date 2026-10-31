*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 4: Ghost in the Machine](https://dev.to/challenges/hacktoberfest-week4-2026-10-26)*

## What I Built

In Maharashtra, where I live, we have **Pitru Paksha** — a fortnight each year when we cook our ancestors' favourite dishes and set a place for them, because the line between the living and the dead gets a little thinner. Reading this week's theme, I realised Día de los Muertos and its *ofrenda* (altar) are the same idea wearing marigolds: a photo, some candles, their favourite food, and an open door.

So I built **Ghostlight** — a digital ofrenda that lives entirely on your own machine.

You leave four things on the altar:

- a **name**,
- who they were to you,
- an **offering** (their favourite food) and a **song** that brings them back,
- and one **memory**.

Then the ghost in the machine — **Gemma 3, Google's open-weight model, running 100% locally** through llama.cpp — finds the words:

- **Remembrance mode:** the keeper of the altar writes a short, warm remembrance.
- **Séance mode:** the ghost answers back — a short first-person message, as if they noticed the candle and spoke one last time.

Every altar you light is saved in a plain JSON file on your own disk, so it's still there next year. Delete the file and it's gone. The dead keep no backups.

## Demo

One command lights the whole thing (first run downloads llama.cpp + the Gemma weights, ~0.85 GB):

```bash
git clone https://github.com/awejofficial/ghostlight.git
cd ghostlight
bash run.sh
# → http://localhost:8000
```

Here is a real altar I lit while building it — for my Aaji (grandmother): puran poli and warm milk as the offering, the old abhang she hummed as the song, and evenings counting the first stars on our terrace in Phaltan as the memory. Every word below is **verbatim output** from Gemma 3 1B running on a CPU, offline:

**Remembrance mode**

> The air smells of marigolds, a slow, fragrant offering to you. Aaji's presence here feels like the twilight deepening, a gentle hush settling over the space. You've lit a small flame, a single point of warmth in this quiet moment.
>
> I remember your hands, steady and sure, tracing the patterns of the evening sky with a worn book. You taught me to read the constellations, to find stories in the shifting light. Puran poli, warm and comforting, nestled beside the milk, a symbol of her love.
>
> You hummed an old abhang song, a melody of longing and resilience, while rolling rotis. I recall evenings spent on the terrace in Phaltan, your watchful gaze fixed on the first stars, each one a silent, watchful guardian.
>
> Now, as the candles burn, you are with us again, a warmth that lingers in the quiet.

**Séance mode**

> The scent of puran poli warms my heart, doesn't it? It reminds me of you, of the way you always held my hand and pointed out the constellations. You taught me to read the evening sky, to find the stories in the clouds. Aaji loved her rotis, especially warm milk – a simple comfort, really. I still remember those afternoons on the terrace in Phaltan, your humming a steady rhythm, counting the stars. You always said each one held a watchful eye, a silent blessing. It feels like a whisper now, a gentle echo of your warmth.
>
> Your name, always.

Yes — the 1B ghost fumbled the sign-off ("Your name" instead of hers). I kept it in. A séance that never slips wouldn't feel like a 1-billion-parameter spirit summoned onto a laptop fan; and the rules of a good altar include not putting words in the dead's mouth, even to fix their grammar.

## Code

{% github awejofficial/ghostlight %}

The full source is on GitHub: [awejofficial/ghostlight](https://github.com/awejofficial/ghostlight) — one Python file for the server (`app.py`, standard library only), three small front-end files, and a `run.sh` that fetches llama.cpp + the Gemma weights and lights the altar.

## How I Built It

The whole stack is deliberately small — the ghost should be able to live on any laptop:

| Piece | What it is |
|---|---|
| Model | **Gemma 3 1B Instruct**, open weights, `Q4_K_M` GGUF (~0.8 GB) |
| Inference | **llama.cpp** `llama-server`, OpenAI-compatible API on localhost |
| App | Python 3 standard library only — `http.server`, zero pip installs |
| Front end | Vanilla HTML/CSS/JS: flickering CSS candle flames, falling marigold petals, a typewriter reveal for the ghost's words |
| Storage | One local file, `data/altars.json` |

A single `./run.sh` downloads llama.cpp and the Gemma weights (both git-ignored), starts the model server, waits for its health check, and serves the altar on `http://localhost:8000`.

The interesting part was the prompting. A 1B model left alone writes greeting-card mush, so the app plays "keeper of the altar": a system prompt that fixes the voice (warm, specific, no preamble), and a user prompt built from the offerings. The specificity is the trick — a model that knows about the puran poli and the terrace stars writes a remembrance; a model that only knows "my grandmother" writes a card.

Full honesty: I built this with an AI agent (Muse) as my pair — it wrote code with me, ran the model, and tested the altar end to end. The challenge rules explicitly allow AI tools, and the "show your work" spirit of this series is exactly why I'm saying it plainly. The idea, the theme interpretation, the demo altar and the final calls are mine.

## Why Does Open Innovation Matter?

Because of what an ofrenda *is*. The things you type into Ghostlight — your grandmother's name, the song she hummed, the memory you can't say out loud — are among the most private sentences a person ever writes. A closed API would mean sending them to a stranger's server, under a stranger's retention policy, at a stranger's price, until the day the service shuts down and takes the altar with it.

Open weights changed every part of that:

- **Privacy by architecture, not by policy.** The model is a file on your disk. There is no server to trust because there is no server.
- **It works with the lights off.** No internet, no account, no API key — it runs on a mid-range laptop CPU during a power cut, which in a Phaltan summer is not a hypothetical.
- **It costs nothing, forever.** Grief shouldn't have a subscription tier.
- **The ghost can change its voice.** One flag swaps Gemma 3 1B for the 4B or 12B; one flag swaps in any other GGUF model. A closed API decides how your dead are allowed to sound. An open one doesn't.
- **It will outlive its demo.** Hosted demos rot. This repo plus two downloadable files will still light a candle in ten years — which is kind of the point of an altar.

## The Spirit of It

The moment it landed wasn't technical. I lit the demo altar for my Aaji, picked séance mode mostly to test the prompt, and the little 1B model — running on a fan-noisy laptop, offline — answered in her voice with a line about the first stars over the terrace. It wasn't perfect. It was *specific*, and specific is what makes you cry at an altar.

That's what "Ghost in the Machine" means to me: not a haunted terminal, but the oldest human use for a machine that talks — asking it to keep someone present a little longer. The ghost was never in the machine. It's in the memory. The machine just holds the candle.

## Prize Categories

- **Best Use of Gemma** — Gemma 3 is the heart of the project: the entire experience is a local, open-weight Gemma 3 1B served by llama.cpp, chosen specifically because the open weights make the privacy and offline behaviour possible.
