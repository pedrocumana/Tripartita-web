# Tripartita de IA

Este proyecto simula una conversación entre varias inteligencias artificiales con una estructura de debate:

- IA_Pro: defiende la automatización y la eficiencia.
- IA_Critica: cuestiona riesgos, límites y ética.
- IA_Moderadora: organiza y resume la conversación.

Puedes usarlo en dos modos:

1. `user_defined`: tú defines el tema.
2. `autonomous`: las IAs generan un tema y discuten por sí mismas.

## Ejecución

```bash
python main.py --mode user_defined --topic "¿Debe una empresa usar IA para automatizar atención al cliente?" --turns 6
```

```bash
python main.py --mode autonomous --turns 6
```

## Conexión con API real

Puedes activar un proveedor real usando variables de entorno:

- `AI_PROVIDER=openai` y `OPENAI_API_KEY=...`
- o `AI_PROVIDER=gemini` y `GEMINI_API_KEY=...`

Ejemplo:

```bash
copy .env.example .env
```

Luego edita `.env` con tus claves.

## Nota

Si no hay clave de API configurada, el script funciona en modo local con respuestas simuladas para seguir probando el flujo de la tripartita.
