import json
import time
from google import genai
from google.genai import types

from config import EXPERIMENTS
from prompt import SYSTEM_INSTRUCTION, USER_PROMPT_TEMPLATE


def _extract_json(text: str) -> dict:
    """Converte a resposta em JSON, tolerando cercas Markdown ocasionais."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
    return json.loads(cleaned)


def run_experiments(document_text: str, api_key: str) -> list[dict]:
    client = genai.Client(api_key=api_key)
    results = []

    for experiment in EXPERIMENTS:
        started = time.time()
        result = {
            "experiment": experiment["name"],
            "model": experiment["model"],
            "parameters": {
                "temperature": experiment["temperature"],
                "top_p": experiment["top_p"],
                "top_k": experiment["top_k"],
            },
        }
        try:
            response = client.models.generate_content(
                model=experiment["model"],
                contents=USER_PROMPT_TEMPLATE.format(document_text=document_text),
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=experiment["temperature"],
                    top_p=experiment["top_p"],
                    top_k=experiment["top_k"],
                    response_mime_type="application/json",
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
