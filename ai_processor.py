import json
import time
from google import genai
from google.genai import types

from config import EXPERIMENTS
from prompt import SYSTEM_INSTRUCTION, USER_PROMPT_TEMPLATE


def _extract_json(text: str) -> dict:
    """Converte a resposta em JSON, tolerando cercas Markdown ocasionais."""
    cleaned = (text or "").strip()
    if not cleaned:
        raise ValueError("O modelo retornou uma resposta vazia.")

    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        parsed = json.loads(cleaned[start : end + 1])

    if isinstance(parsed, list) and len(parsed) == 1 and isinstance(parsed[0], dict):
        parsed = parsed[0]

    if not isinstance(parsed, dict):
        raise ValueError(f"Esperado objeto JSON (dict), mas o modelo retornou {type(parsed).__name__}.")

    return parsed


def run_experiments(document_text: str, api_key: str) -> list[dict]:
    clean_key = (api_key or "").strip()
    if not clean_key:
        raise ValueError("Chave da API Gemini não informada.")

    client = genai.Client(api_key=clean_key)
    results = []

    for experiment in EXPERIMENTS:
        started = time.time()
        params = {
            key: experiment[key]
            for key in ("temperature", "top_p", "top_k")
            if experiment.get(key) is not None
        }
        result = {
            "experiment": experiment["name"],
            "model": experiment["model"],
            "parameters": params,
        }
        try:
            response = client.models.generate_content(
                model=experiment["model"],
                contents=USER_PROMPT_TEMPLATE.format(document_text=document_text),
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    response_mime_type="application/json",
                    **params,
                ),
            )
            raw_text = response.text or ""
            result["data"] = _extract_json(raw_text)
            result["raw_response"] = raw_text
        except Exception as exc:
            result["error"] = f"{type(exc).__name__}: {exc}"
        result["duration_seconds"] = time.time() - started
        results.append(result)

    return results
