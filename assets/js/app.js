"use strict";
const menuButton = document.querySelector("#menu-toggle");
menuButton?.addEventListener("click", () => {
  const expanded = menuButton.getAttribute("aria-expanded") !== "true";
  menuButton.setAttribute("aria-expanded", String(expanded));
  menuButton.setAttribute("aria-label", expanded ? "Fechar menu" : "Abrir menu");
  document.querySelector("#menu").classList.toggle("open", expanded);
});

document.querySelectorAll("details.question-preview").forEach(detail => {
  if (location.hash === `#${detail.id}`) detail.open = true;
});

const planForm = document.querySelector("#plan-form");
if (planForm) {
  const kind = planForm.querySelector("[name=kind]");
  function updateFields() {
    const schedule = kind.value === "schedule";
    for (const name of ["day", "time"]) {
      const field = planForm.querySelector(`[data-plan-field=${name}]`);
      field.hidden = !schedule;
      const input = field.querySelector("input, select");
      input.required = schedule;
      input.disabled = !schedule;
    }
    const due = planForm.querySelector("[data-plan-field=due]");
    due.hidden = schedule || kind.value === "task";
    due.querySelector("input").required = kind.value === "reminder";
    due.querySelector("input").disabled = due.hidden;
  }
  kind.addEventListener("change", updateFields);
  updateFields();
}

// O relógio usa um prazo absoluto: abas em segundo plano não acumulam atraso.
const timerWidget = document.querySelector("[data-timer]");
if (timerWidget) {
  const key = `trilha-timer-${document.body.dataset.user}`;
  const focusInput = document.querySelector("#focus-minutes");
  const breakInput = document.querySelector("#break-minutes");
  const display = document.querySelector("#timer-display");
  const status = document.querySelector("#timer-status");
  const startButton = document.querySelector("#timer-start");
  let state = {mode:"focus", focus:25, break:5, remaining:1500, deadline:null, finished:false};
  try {
    const saved = JSON.parse(sessionStorage.getItem(key));
    if (saved && ["focus", "break"].includes(saved.mode) && Number.isFinite(saved.remaining)
        && saved.focus >= 1 && saved.focus <= 240 && saved.break >= 1 && saved.break <= 60
        && (saved.deadline === null || Number.isFinite(saved.deadline))) state = saved;
  } catch (_) { /* O temporizador funciona mesmo com armazenamento desabilitado. */ }
  focusInput.value = state.focus;
  breakInput.value = state.break;
  function persist() {
    try { sessionStorage.setItem(key, JSON.stringify(state)); } catch (_) { /* Sem persistência. */ }
  }
  function secondsLeft() {
    return state.deadline ? Math.max(0, Math.ceil((state.deadline - Date.now()) / 1000)) : state.remaining;
  }
  function draw() {
    const left = secondsLeft();
    if (state.deadline && left === 0) {
      state.deadline = null;
      state.remaining = 0;
      state.finished = true;
      persist();
    }
    display.textContent = `${String(Math.floor(left / 60)).padStart(2,"0")}:${String(left % 60).padStart(2,"0")}`;
    startButton.textContent = state.deadline ? "Pausar" : state.finished ? "Iniciar novamente" : "Iniciar";
    status.textContent = state.finished ? (state.mode === "focus" ? "Estudo concluído. Hora de uma pausa!" : "Pausa concluída. Pronto para estudar?")
      : state.deadline ? (state.mode === "focus" ? "Estudo em andamento." : "Aproveite sua pausa.") : "Pronto para começar.";
    focusInput.disabled = breakInput.disabled = Boolean(state.deadline);
    document.querySelectorAll("[data-mode]").forEach(button => button.setAttribute("aria-pressed", String(button.dataset.mode === state.mode)));
  }
  startButton.addEventListener("click", () => {
    if (state.deadline) { state.remaining = secondsLeft(); state.deadline = null; }
    else {
      if (state.finished || !state.remaining) state.remaining = state[state.mode] * 60;
      state.finished = false;
      state.deadline = Date.now() + state.remaining * 1000;
    }
    persist(); draw();
  });
  function reset() { state.deadline = null; state.remaining = state[state.mode] * 60; state.finished = false; persist(); draw(); }
  document.querySelector("#timer-reset").addEventListener("click", reset);
  document.querySelectorAll("[data-mode]").forEach(button => button.addEventListener("click", () => {
    if (state.mode !== button.dataset.mode) { state.mode = button.dataset.mode; reset(); }
  }));
  [[focusInput,"focus",240],[breakInput,"break",60]].forEach(([input,mode,max]) => input.addEventListener("change", () => {
    const value = Number(input.value);
    if (!Number.isInteger(value) || value < 1 || value > max) { input.value = state[mode]; return; }
    state[mode] = value;
    if (state.mode === mode) reset();
    else persist();
  }));
  draw();
  setInterval(draw, 250);
  document.addEventListener("visibilitychange", draw);
}

const reminderBox = document.querySelector("#live-reminders");
if (reminderBox && document.body.dataset.user !== "visitante") {
  async function refreshReminders() {
    try {
      const response = await fetch(reminderBox.dataset.endpoint, {headers:{"Accept":"application/json"}, cache:"no-store"});
      if (!response.ok) return;
      const data = await response.json();
      const fragment = document.createDocumentFragment();
      for (const reminder of data.reminders) {
        const notice = document.createElement("div");
        notice.className = "notice live-reminder";
        const text = document.createElement("span"); text.textContent = `Lembrete: ${reminder.title}`;
        const link = document.createElement("a"); link.href = "/tecnicas.html#organizacao";
        link.className = "text-link"; link.textContent = "Ver lembretes →";
        notice.append(text, link); fragment.append(notice);
      }
      // Evita anunciar novamente o mesmo lembrete a cada consulta.
      const ids = JSON.stringify(data.reminders);
      if (reminderBox.dataset.last !== ids) { reminderBox.replaceChildren(fragment); reminderBox.dataset.last = ids; }
    } catch (_) { /* A próxima consulta tentará novamente. */ }
  }
  refreshReminders();
  setInterval(refreshReminders, 30000);
}
