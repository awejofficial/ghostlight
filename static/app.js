(() => {
  const $ = (sel) => document.querySelector(sel);
  const form = $("#light-form");
  const btn = $("#light-btn");
  const errBox = $("#form-error");
  const altarPanel = $("#altar-panel");
  const galleryBox = $("#gallery");

  // Falling marigold petals (cempasuchil), to guide the spirits home.
  const petalsBox = $("#petals");
  for (let i = 0; i < 14; i++) {
    const p = document.createElement("span");
    p.className = "petal";
    const size = 8 + Math.random() * 10;
    p.style.width = size + "px";
    p.style.height = size * 0.82 + "px";
    p.style.left = Math.random() * 100 + "vw";
    p.style.animationDuration = 11 + Math.random() * 14 + "s";
    p.style.animationDelay = -Math.random() * 18 + "s";
    petalsBox.appendChild(p);
  }

  async function checkGhost() {
    const el = $("#model-status");
    try {
      const r = await fetch("/api/health");
      const d = await r.json();
      if (d.model === "ok") {
        el.textContent = "🕯️ The ghost is home — Gemma is running locally on this machine.";
        el.className = "status ok";
      } else {
        el.textContent = "The ghost is not home yet — start the local model with ./run.sh, then refresh.";
        el.className = "status down";
      }
    } catch {
      el.textContent = "";
    }
  }

  function typeWords(el, text) {
    el.textContent = "";
    const words = text.split(/(\s+)/);
    let i = 0;
    const tick = () => {
      if (i >= words.length) return;
      el.textContent += words.slice(i, i + 3).join("");
      i += 3;
      setTimeout(tick, 28);
    };
    tick();
  }

  function showAltar(a) {
    $("#altar-name").textContent = a.name;
    $("#altar-relation").textContent = a.relation || "";
    const off = $("#altar-offerings");
    off.innerHTML = "";
    if (a.food) {
      const s = document.createElement("span");
      s.className = "offering";
      s.textContent = "🍞 " + a.food;
      off.appendChild(s);
    }
    if (a.song) {
      const s = document.createElement("span");
      s.className = "offering";
      s.textContent = "🎵 " + a.song;
      off.appendChild(s);
    }
    $("#altar-mode").textContent =
      a.mode === "seance"
        ? "séance mode — the ghost spoke in the first person"
        : "a remembrance, written by the keeper of the altar";
    altarPanel.classList.remove("hidden");
    typeWords($("#altar-words"), a.words);
    altarPanel.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  async function loadGallery() {
    try {
      const r = await fetch("/api/altars");
      const d = await r.json();
      galleryBox.innerHTML = "";
      if (!d.altars.length) {
        galleryBox.innerHTML = '<p class="gallery-empty">No candles yet. The altar is waiting.</p>';
        return;
      }
      for (const a of d.altars) {
        const card = document.createElement("button");
        card.className = "card";
        const when = a.lit_at ? new Date(a.lit_at).toLocaleString() : "";
        card.innerHTML = "";
        const n = document.createElement("span");
        n.className = "card-name";
        n.textContent = "🕯️ " + a.name;
        const m = document.createElement("span");
        m.className = "card-meta";
        m.textContent = (a.mode === "seance" ? "séance" : "remembrance") + (when ? " · " + when : "");
        card.appendChild(n);
        card.appendChild(m);
        card.addEventListener("click", () => showAltar(a));
        galleryBox.appendChild(card);
      }
    } catch {
      galleryBox.innerHTML = '<p class="gallery-empty">The gallery could not be reached.</p>';
    }
  }

  form.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    errBox.textContent = "";
    const data = Object.fromEntries(new FormData(form).entries());
    btn.disabled = true;
    const old = btn.textContent;
    btn.textContent = "The ghost is gathering its words…";
    try {
      const r = await fetch("/api/light", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      const d = await r.json();
      if (!r.ok) throw new Error(d.error || "Something went wrong.");
      showAltar(d.altar);
      loadGallery();
    } catch (e) {
      errBox.textContent = e.message;
    } finally {
      btn.disabled = false;
      btn.textContent = old;
    }
  });

  checkGhost();
  loadGallery();
})();
