"""Métricas para comparar os experimentos.

1. Diagnóstico das seções: quantas o modelo considerou presentes, parciais ou ausentes.
2. Verificação de evidências: confere se cada trecho citado pelo modelo existe
   de fato no documento. Mede invenção (alucinação) sem nova chamada à API.
"""
import re
import unicodedata

import pandas as pd


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(c for c in text if not unicodedata.combining(c)).lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _evidence_found(trecho: str, normalized_document: str) -> bool:
    trecho_norm = _normalize(trecho)
    if not trecho_norm:
        return False
    if trecho_norm in normalized_document:
        return True
    # Tolera reticências ou cortes: aceita se todos os fragmentos de 4+ palavras existirem.
    fragments = [f for f in re.split(r"\s*(?:\.\.\.|…)\s*", trecho or "") if len(f.split()) >= 4]
    return bool(fragments) and all(_normalize(f) in normalized_document for f in fragments)


def check_evidences(data: dict, document_text: str) -> dict:
    """Marca cada evidência com `verificada` (True/False) e devolve o resumo."""
    normalized_document = _normalize(document_text)
    total = found = 0
    for item in data.get("resultado_esperado_gerado", {}).get("itens", []):
        for evidence in item.get("evidencias", []):
            ok = _evidence_found(evidence.get("trecho", ""), normalized_document)
            evidence["verificada"] = ok
            total += 1
            found += ok
    return {"total": total, "verificadas": found}


def compare_results(results: list[dict]) -> pd.DataFrame:
    rows = []
    for result in results:
        data = result.get("data") or {}
        status = [s.get("status") for s in data.get("diagnostico_secoes", [])]
        items = data.get("resultado_esperado_gerado", {}).get("itens", [])
        ev = result.get("evidence_check", {})
        params = result.get("parameters") or {}
        rows.append({
            "Experimento": result["experiment"],
            "Modelo": result.get("model", ""),
            "Parâmetros": ", ".join(f"{k}={v}" for k, v in params.items()) or "—",
            "Seções presentes": status.count("presente"),
            "Parciais / só referência": status.count("parcial") + status.count("apenas referência"),
            "Ausentes": status.count("ausente"),
            "Itens gerados": len(items),
            "Evidências verificadas": f"{ev['verificadas']}/{ev['total']}" if ev else "—",
            "Melhor no geral": (data.get("comparacao") or {}).get("melhor_no_geral", "sem seção original")
            if data
            else "—",
            "Tempo (s)": round(result.get("duration_seconds", 0), 1),
            "Status": "Erro" if result.get("error") else "Concluído",
        })
    return pd.DataFrame(rows)
