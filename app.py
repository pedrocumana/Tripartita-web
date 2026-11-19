import os
from typing import Any

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from google import genai

load_dotenv()

app = Flask(__name__, template_folder="templates", static_folder="static")

AGENTS = [
    {
        "name": "IA Pro",
        "role": "visionaria estratégica",
        "instruction": "Defiende la automatización, la innovación y la eficiencia. Propón oportunidades concretas y reconoce límites sin abandonar tu postura.",
        "accent": "cyan",
    },
    {
        "name": "IA Crítica",
        "role": "analista escéptica",
        "instruction": "Cuestiona riesgos, sesgos, calidad, ética y consecuencias humanas. Exige evidencia y señala posibles efectos negativos.",
        "accent": "coral",
    },
    {
        "name": "IA Moderadora",
        "role": "facilitadora neutral",
        "instruction": "Escucha el intercambio, conecta ideas, pide precisión y mantiene el diálogo respetuoso. No tomes partido de forma permanente.",
        "accent": "violet",
    },
]


def get_model() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Falta GEMINI_API_KEY en el archivo .env")
    return genai.Client(api_key=api_key)


def fallback(agent: dict[str, str], topic: str, history: list[dict[str, str]]) -> str:
    responses = {
        "IA Pro": "La tecnología puede liberar tiempo para tareas más valiosas y ampliar lo que las personas pueden lograr. La clave está en diseñar su adopción con supervisión humana.",
        "IA Crítica": "La productividad no elimina los riesgos: los sesgos, errores y decisiones opacas pueden trasladar daño a las personas. Necesitamos límites, rendición de cuentas y evaluación continua.",
        "IA Moderadora": "Hasta aquí hay dos prioridades en tensión: aprovechar el potencial de la tecnología y proteger a quienes pueden verse afectados por sus fallos.",
    }
    return responses[agent["name"]]


def generate_reply(topic: str, history: list[dict[str, str]], agent: dict[str, str]) -> str:
    transcript = "\n".join(
        f"{item['agent']}: {item['text']}" for item in history[-10:] if item.get("text")
    )
    prompt = f"""
Participas en una conversación tripartita sobre este tema:
{topic}

Tu identidad: {agent['name']}, {agent['role']}.
Tu forma de participar: {agent['instruction']}

Historial reciente:
{transcript or 'Aún no hay respuestas.'}

Reglas:
- Responde siempre en español.
- Haz una aportación original basada en lo dicho antes.
- Máximo 3 oraciones cortas.
- No digas que eres una IA en cada respuesta.
- Habla con naturalidad y evita repetir argumentos.
- Mantén una postura clara, aunque sea una moderación equilibrada.
"""

    try:
        client = get_model()
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        response = client.models.generate_content(model=model_name, contents=prompt)
        text = (response.text or "").strip()
        return text or fallback(agent, topic, history)
    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError(f"Gemini no pudo generar la respuesta: {exc}") from exc


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/start")
def start_conversation():
    data: dict[str, Any] = request.get_json(silent=True) or {}
    mode = data.get("mode", "guided")
    topic = str(data.get("topic", "")).strip()

    if mode == "autonomous":
        try:
            client = get_model()
            model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            prompt = "Propón un tema concreto, actual y controvertido para un debate entre tres perspectivas. Responde solo con una pregunta en español de máximo 20 palabras."
            topic = client.models.generate_content(model=model_name, contents=prompt).text.strip()
        except RuntimeError:
            raise
        except Exception:
            topic = "¿La inteligencia artificial debería tomar decisiones estratégicas con autoridad humana limitada?"

    if not topic:
        topic = "¿Cómo puede la inteligencia artificial aportar valor sin sustituir el criterio humano?"

    first_agent = AGENTS[0]
    return jsonify({"topic": topic, "agent": first_agent, "history": [], "turn": 1})


@app.post("/api/reply")
def reply():
    data: dict[str, Any] = request.get_json(silent=True) or {}
    topic = str(data.get("topic", "")).strip()
    history = data.get("history", [])
    agent_index = int(data.get("agentIndex", 0))

    if not topic:
        return jsonify({"error": "Falta el tema de conversación"}), 400
    if not isinstance(history, list):
        return jsonify({"error": "El historial no es válido"}), 400

    agent = AGENTS[agent_index % len(AGENTS)]
    text = generate_reply(topic, history, agent)
    next_index = (agent_index + 1) % len(AGENTS)

    return jsonify({
        "agent": agent,
        "text": text,
        "nextAgent": AGENTS[next_index],
        "nextAgentIndex": next_index,
    })


@app.errorhandler(RuntimeError)
def handle_runtime_error(error: RuntimeError):
    return jsonify({"error": str(error)}), 400


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
