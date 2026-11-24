import pandas as pd


def compare_results(results: list[dict]) -> pd.DataFrame:
    rows = []
    for result in results:
        data = result.get("data", {})
        attributes = data.get("atributos", data)
        identified = 0
        partial = 0
        missing = 0

        if isinstance(attributes, dict):
            for key, value in attributes.items():
                if isinstance(value, dict):
                    status = str(value.get("status", "")).lower()
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
