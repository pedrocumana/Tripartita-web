import argparse
import os
import random
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Agent:
    name: str
    role: str
    personality: str
    objective: str


def build_agents() -> List[Agent]:
    return [
        Agent(
            name="IA_Pro",
            role="Defensa la automatización",
            personality="Piensas desde la eficiencia, la velocidad y la escalabilidad.",
            objective="Argumenta por qué la IA puede optimizar procesos y reducir costos.",
        ),
        Agent(
            name="IA_Critica",
            role="Cuestiona la automatización",
            personality="Te enfocas en riesgos, ética, calidad y sesgos.",
            objective="Apunta los límites, errores y consecuencias negativas.",
        ),
        Agent(
            name="IA_Moderadora",
            role="Dirige la conversación",
            personality="Eres neutral y buscas claridad, síntesis y orden.",
            objective="Resumir los puntos clave y pedir precisión cuando el debate se vuelve confuso.",
        ),
    ]


def build_topic_bank() -> List[str]:
    return [
        "¿La IA debería reemplazar tareas repetitivas en el trabajo humano?",
        "¿Es útil usar IA para atención al cliente o empeora la experiencia?",
        "¿Puede la IA crear arte auténtico o solo imitar estilos?",
        "¿La IA debe tomar decisiones en educación y salud con supervisión humana?",
        "¿La automatización con IA aumenta la productividad o destruye empleo?",
    ]


def choose_topic(mode: str, custom_topic: Optional[str]) -> str:
    if custom_topic:
        return custom_topic
    if mode == "autonomous":
        topic = random.choice(build_topic_bank())
        return f"Las IAs han decidido discutir este tema: {topic}"
    return "Tema propuesto por el usuario: ¿La IA puede mejorar la creatividad sin reemplazar al ser humano?"


def fallback_response(agent: Agent, topic: str, history: List[str]) -> str:
    if agent.name == "IA_Pro":
        return (
            "La IA puede acelerar tareas repetitivas, reducir costos y permitir que las personas se concentren en "
            "trabajo más estratégico. Si se usa bien, complementa al ser humano y mejora la eficiencia."
        )
    if agent.name == "IA_Critica":
        return (
            "El problema no es solo la velocidad, sino la calidad de la decisión. La IA puede cometer errores, simplificar "
            "situaciones complejas y reforzar sesgos si no hay supervisión humana adecuada."
        )
    return (
        f"Desde la moderación, el punto central es este: {topic}. Lo más relevante es separar lo que la IA hace bien de "
        "lo que aún requiere criterio humano, responsabilidad y claridad de límites."
    )


def generate_response(agent: Agent, topic: str, history: List[str]) -> str:
    provider = os.getenv("AI_PROVIDER", "local").lower()
    prompt = (
        f"Eres {agent.name}. {agent.persona}. "
        f"Tu rol es {agent.role}. Objetivo: {agent.objective}.\n\n"
        f"Tema de discusión: {topic}\n\nHistorial:\n" + "\n".join(history[-5:])
    )

    if provider == "openai" and os.getenv("OPENAI_API_KEY"):
        try:
            import openai

            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            completion = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": "Responde en 2 a 4 frases, con una postura clara y concreta."},
                ],
                temperature=0.8,
            )
            return completion.choices[0].message.content.strip()
        except Exception:
            pass

    if provider == "gemini" and os.getenv("GEMINI_API_KEY"):
        try:
            import google.generativeai as genai

            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            model = genai.GenerativeModel(model_name=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"))
            response = model.generate_content(prompt + "\n\nResponde en 2 a 4 frases, con una postura clara y concreta.")
            return response.text.strip()
        except Exception:
            pass

    return fallback_response(agent, topic, history)


def run_tripartite(topic: Optional[str] = None, mode: str = "user_defined", max_turns: int = 6) -> None:
    agents = build_agents()
    chosen_topic = choose_topic(mode, topic)
    history: List[str] = [f"Tema: {chosen_topic}"]

    print("=" * 80)
    print("TRIPARTITA DE INTELIGENCIAS ARTIFICIALES")
    print("=" * 80)
    print(f"Modo: {mode}")
    print(f"Tema: {chosen_topic}")
    print("=" * 80)

    for index in range(max_turns):
        agent = agents[index % len(agents)]
        reply = generate_response(agent, chosen_topic, history)
        message = f"[{agent.name}] {reply}"
        history.append(message)
        print(f"\n{message}")

        if index == max_turns - 1:
            summary = (
                f"[{agents[2].name}] En resumen, el debate se centra en tres puntos: la productividad que ofrece la IA, "
                "los riesgos de errores y sesgos, y la necesidad de mantener supervisión humana para que la tecnología sirva "
                "a las personas y no las reemplace sin criterio."
            )
            print(f"\n{summary}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simula una tripartita entre dos o más IAs.")
    parser.add_argument("--mode", choices=["user_defined", "autonomous"], default="user_defined")
    parser.add_argument("--topic", type=str, default=None, help="Tema propuesto por el usuario.")
    parser.add_argument("--turns", type=int, default=6, help="Número de turnos de conversación.")
    args = parser.parse_args()

    run_tripartite(topic=args.topic, mode=args.mode, max_turns=args.turns)
