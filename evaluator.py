import pandas as pd


def compare_results(results: list[dict]) -> pd.DataFrame:
    rows = []
    for result in results:
        data = result.get("data")
        if not isinstance(data, dict):
            data = {}
        attributes = data.get("atributos")
        if not isinstance(attributes, dict):
            attributes = data

        identified = 0
        partial = 0
        missing = 0

        for value in attributes.values():
            if isinstance(value, dict) and "status" in value:
                status = str(value.get("status", "")).strip().lower()
                if status == "identificado":
                    identified += 1
                elif status == "parcial":
                    partial += 1
                elif status in ("não identificado", "nao identificado"):
                    missing += 1

        rows.append({
            "Experimento": result["experiment"],
            "Modelo": result.get("model", ""),
            "Identificados": identified,
            "Parciais": partial,
            "Não identificados": missing,
            "Tempo (s)": round(result.get("duration_seconds", 0), 1),
            "Status": "Erro" if result.get("error") else "Concluído",
        })
    return pd.DataFrame(rows)
