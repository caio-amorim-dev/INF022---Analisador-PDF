import json
from pathlib import Path
import streamlit as st

from pdf_reader import extract_pdf_pages
from ai_processor import run_experiments
from evaluator import compare_results
from config import EXPERIMENTS

st.set_page_config(page_title="Analisador de PDF com IA", page_icon="📄", layout="wide")
st.title("Analisador de PDF com IA")
st.write("Extrai atributos de um documento, gera a seção **Resultado Esperado** e compara três configurações de IA.")

with st.sidebar:
    st.header("Acesso à API")
    api_key = st.text_input(
        "Google Gemini API Key",
        type="password",
        help="A chave é usada apenas durante esta execução. Não a publique nem a envie a terceiros.",
    )
    st.caption("Crie uma chave no Google AI Studio. O projeto usa a API Gemini.")

uploaded = st.file_uploader("Envie o PDF para análise", type=["pdf"])

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

    if st.button("Executar os 3 experimentos", type="primary", disabled=not api_key or not full_text.strip()):
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
    st.dataframe(compare_results(results), use_container_width=True, hide_index=True)

    for result in results:
        with st.expander(f"{result['experiment']} — {result.get('model', '')}", expanded=True):
            if result.get("error"):
                st.error(result["error"])
                continue
            data = result["data"]
            st.markdown("**Resultado Esperado**")
            st.write(data.get("resultado_esperado", "Não identificado no documento."))
            st.markdown("**Possíveis inconsistências**")
            issues = data.get("inconsistencias", [])
            if issues:
                for issue in issues:
                    st.warning(issue)
            else:
                st.write("Nenhuma inconsistência explicitamente apontada pelo modelo.")
            with st.expander("Ver extração estruturada (JSON)"):
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
elif not api_key:
    st.info("Informe sua chave API na barra lateral para habilitar a análise.")
