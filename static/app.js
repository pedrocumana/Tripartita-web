const state = {
  mode: "guided",
  topic: "",
  history: [],
  agentIndex: 0,
  turn: 0,
  paused: false,
  running: false,
};

const topic = document.querySelector("#topic");
const topicLabel = document.querySelector("#topicLabel");
const topicTitle = document.querySelector("#topicTitle");
const startButton = document.querySelector("#startButton");
const autoButton = document.querySelector("#autoButton");
const pauseButton = document.querySelector("#pauseButton");
const resetButton = document.querySelector("#resetButton");
const messages = document.querySelector("#messages");
const turnStatus = document.querySelector("#turnStatus");

function setStatus(text, live = false) {
  turnStatus.innerHTML = `<span class="status-dot${live ? " live" : ""}"></span><span>${text}</span>`;
}

function escapeHtml(value) {
  const node = document.createElement("div");
  node.textContent = value;
  return node.innerHTML;
}

function agentInitial(name) {
  return name.replace("IA ", "").charAt(0).toUpperCase();
}

function agentAccent(agent) {
  return agent.accent || "violet";
}

function removeEmptyState() {
  const empty = messages.querySelector(".empty-state");
  if (empty) empty.remove();
}

function addTyping(agent) {
  removeEmptyState();
  const element = document.createElement("div");
  element.className = "message typing-message";
  element.innerHTML = `
    <span class="avatar ${agentAccent(agent)}">${escapeHtml(agentInitial(agent.name))}</span>
    <div class="bubble"><div class="typing"><i></i><i></i><i></i></div></div>`;
  messages.appendChild(element);
  messages.scrollTop = messages.scrollHeight;
  return element;
}

function addMessage(agent, text) {
  const element = document.createElement("div");
  element.className = "message";
  element.innerHTML = `
    <span class="avatar ${agentAccent(agent)}">${escapeHtml(agentInitial(agent.name))}</span>
    <article class="bubble">
      <div class="message-head"><strong>${escapeHtml(agent.name)}</strong><time>ahora</time></div>
      <p>${escapeHtml(text)}</p>
    </article>`;
  messages.appendChild(element);
  messages.scrollTop = messages.scrollHeight;
}

async function startConversation() {
  if (state.running) return;
  state.running = true;
  startButton.disabled = true;
  startButton.querySelector("span").textContent = "Iniciando…";
  setStatus("Preparando el debate", true);

  try {
    const response = await fetch("/api/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode: state.mode, topic: topic.value }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "No se pudo iniciar");

    state.topic = data.topic;
    state.history = data.history || [];
    state.agentIndex = 0;
    state.turn = 0;
    state.paused = false;
    topicTitle.textContent = data.topic;
    messages.innerHTML = "";
    autoButton.disabled = false;
    pauseButton.disabled = false;
    pauseButton.textContent = "Ⅱ";
    setStatus(`${data.agent.name} va a intervenir`, true);
  } catch (error) {
    setStatus(error.message);
  } finally {
    state.running = false;
    startButton.disabled = false;
    startButton.querySelector("span").textContent = "Iniciar conversación";
  }
}

async function nextTurn() {
  if (state.running || state.paused) return;
  state.running = true;
  autoButton.disabled = true;

  const currentAgent = {
    0: { name: "IA Pro", accent: "cyan" },
    1: { name: "IA Crítica", accent: "coral" },
    2: { name: "IA Moderadora", accent: "violet" },
  }[state.agentIndex];

  const typing = addTyping(currentAgent);
  setStatus(`${currentAgent.name} está pensando`, true);

  try {
    const response = await fetch("/api/reply", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        topic: state.topic,
        history: state.history,
        agentIndex: state.agentIndex,
      }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "No se pudo generar la respuesta");

    typing.remove();
    addMessage(data.agent, data.text);
    state.history.push({ agent: data.agent.name, text: data.text });
    state.agentIndex = data.nextAgentIndex;
    state.turn += 1;
    setStatus(`Turno ${state.turn} · sigue ${data.nextAgent.name}`, true);
  } catch (error) {
    typing.remove();
    setStatus(error.message);
  } finally {
    state.running = false;
    autoButton.disabled = state.paused;
  }
}

function resetConversation() {
  state.topic = "";
  state.history = [];
  state.agentIndex = 0;
  state.turn = 0;
  state.paused = false;
  topicTitle.textContent = "Nueva conversación";
  messages.innerHTML = `
    <div class="empty-state">
      <div class="orb"><span></span><span></span><span></span></div>
      <h2>Un debate inteligente comienza aquí</h2>
      <p>Elige un tema o deja que las tres perspectivas lo encuentren por sí mismas.</p>
    </div>`;
  autoButton.disabled = true;
  pauseButton.disabled = true;
  setStatus("Lista para comenzar");
}

document.querySelectorAll(".mode-button").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".mode-button").forEach((item) => {
      item.classList.remove("active");
      item.setAttribute("aria-checked", "false");
    });
    button.classList.add("active");
    button.setAttribute("aria-checked", "true");
    state.mode = button.dataset.mode;
    if (state.mode === "autonomous") {
      topicLabel.textContent = "Tema generado por las IAs";
      topic.disabled = true;
    } else {
      topicLabel.textContent = "Tema del debate";
      topic.disabled = false;
    }
  });
});

startButton.addEventListener("click", startConversation);
autoButton.addEventListener("click", nextTurn);
resetButton.addEventListener("click", resetConversation);
pauseButton.addEventListener("click", () => {
  state.paused = !state.paused;
  pauseButton.textContent = state.paused ? "▶" : "Ⅱ";
  pauseButton.title = state.paused ? "Reanudar" : "Pausar";
  autoButton.disabled = state.paused;
  setStatus(state.paused ? "Conversación pausada" : `Turno ${state.turn} en curso`, !state.paused);
});
