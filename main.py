import json
import os
from pathlib import Path
import streamlit as st

from pdf_reader import extract_pdf_pages
from ai_processor import run_experiments
from evaluator import compare_results


def _load_default_api_key() -> str:
    """Lê GEMINI_API_KEY do ambiente ou de um arquivo .env na raiz do projeto."""
    env_key = os.getenv("GEMINI_API_KEY", "").strip()
    if env_key:
        return env_key

    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.is_file():
        return ""

    for raw_line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() == "GEMINI_API_KEY":
            return value.strip().strip('"').strip("'")
    return ""


def _extract_expected_result(data: dict) -> str:
    """Extrai o texto de resultado_esperado mesmo se vier aninhado como objeto."""
    expected = data.get("resultado_esperado")
    if isinstance(expected, dict):
        expected = expected.get("sintese") or expected.get("texto")
    if not expected:
        attrs = data.get("atributos")
        if isinstance(attrs, dict) and isinstance(attrs.get("resultado_esperado"), dict):
            expected = attrs["resultado_esperado"].get("sintese")
    if isinstance(expected, str) and expected.strip():
        return expected.strip()
    return "Não identificado no documento."


def _normalize_text_list(value) -> list[str]:
    """Converte listas/strings/objetos em uma lista limpa de textos para exibição."""
    if not value:
        return []
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, list):
        items = []
        for item in value:
            if isinstance(item, str):
                if item.strip():
                    items.append(item.strip())
            elif item is not None:
                items.append(json.dumps(item, ensure_ascii=False))
        return items
    return [json.dumps(value, ensure_ascii=False)]


st.set_page_config(page_title="Analisador de PDF com IA", page_icon="📄", layout="wide")
st.title("Analisador de PDF com IA")
st.write("Extrai atributos de um documento, gera a seção **Resultado Esperado** e compara três configurações de IA.")

with st.sidebar:
    st.header("Acesso à API")
    api_key = st.text_input(
        "Google Gemini API Key",
        value=_load_default_api_key(),
        type="password",
        help="A chave é usada apenas durante esta execução. Não a publique nem a envie a terceiros.",
    )
    st.caption("Crie uma chave no Google AI Studio. O projeto usa a API Gemini.")

uploaded = st.file_uploader("Envie o PDF para análise", type=["pdf"])
full_text = ""

if uploaded:
    pdf_bytes = uploaded.getvalue()
    try:
        pages = extract_pdf_pages(pdf_bytes)
        full_text = "\n\n".join(
            f"[PÁGINA {p['page']}]\n{p['text']}" for p in pages if p["text"].strip()
        )
        st.success(f"PDF lido: {len(pages)} página(s), {len(full_text):,} caracteres extraídos.")
        with st.expander("Prévia do texto extraído"):
            st.text(full_text[:12000] or "Nenhum texto foi extraído. O PDF pode ser digitalizado como imagem.")
        if not full_text.strip():
            st.warning("Não foi possível extrair texto. Este protótipo não faz OCR; use um PDF pesquisável.")
    except Exception as exc:
        st.error(f"Erro ao ler o PDF: {exc}")
        st.stop()

    if st.button("Executar os 3 experimentos", type="primary", disabled=not api_key.strip() or not full_text.strip()):
        with st.spinner("Enviando o conteúdo para os três experimentos. Isso pode levar alguns minutos..."):
            try:
                results = run_experiments(full_text, api_key)
                st.session_state["results"] = results
                st.session_state["source_name"] = uploaded.name
            except Exception as exc:
                st.error(f"Falha na análise: {exc}")
                st.stop()

if "results" in st.session_state:
    results = st.session_state["results"]
    st.divider()
    st.subheader("Comparação dos experimentos")
    st.dataframe(compare_results(results), width="stretch", hide_index=True)

    for result in results:
        with st.expander(f"{result['experiment']} — {result.get('model', '')}", expanded=True):
            if result.get("error"):
                st.error(result["error"])
                continue

            data = result.get("data")
            if not isinstance(data, dict):
                st.warning("O modelo retornou um formato inesperado de dados.")
                st.json(data)
                st.caption(f"Tempo: {result.get('duration_seconds', 0):.1f}s")
                continue

            tab_summary, tab_json = st.tabs(["Resumo", "Extração estruturada (JSON)"])
            with tab_summary:
                st.markdown("**Resultado Esperado**")
                st.write(_extract_expected_result(data))

                st.markdown("**Possíveis inconsistências**")
                issues = _normalize_text_list(data.get("inconsistencias"))
                if issues:
                    for issue in issues:
                        st.warning(issue)
                else:
                    st.write("Nenhuma inconsistência explicitamente apontada pelo modelo.")

                notes = _normalize_text_list(data.get("observacoes"))
                if notes:
                    st.markdown("**Observações**")
                    for note in notes:
                        st.info(note)

            with tab_json:
                st.json(data)

            st.caption(f"Tempo: {result.get('duration_seconds', 0):.1f}s")

    output = {
        "arquivo_origem": st.session_state.get("source_name"),
        "experimentos": results,
    }
    st.download_button(
        "Baixar resultados em JSON",
        data=json.dumps(output, ensure_ascii=False, indent=2),
        file_name="resultados_analise.json",
        mime="application/json",
    )

elif not uploaded:
    st.info("Envie um PDF para começar.")
elif not api_key.strip():
    st.info("Informe sua chave API na barra lateral para habilitar a análise.")
