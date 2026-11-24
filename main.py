import json
import os
from pathlib import Path
import streamlit as st

from document_reader import SUPPORTED_EXTENSIONS, read_document
from ai_processor import run_experiments
from evaluator import check_evidences, compare_results

STATUS_ICON = {"presente": "✅", "parcial": "🟡", "apenas referência": "↪️", "ausente": "❌"}


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


st.set_page_config(page_title="Analisador de Documentos com IA", page_icon="📄", layout="wide")
st.title("Analisador de Documentos com IA")
st.write(
    "Lê o **Entendimento do Objeto** de uma auditoria (PDF, DOCX ou texto colado), redige a seção "
    "**Resultados Esperados** fundamentada no documento e compara três configurações de IA."
)

with st.sidebar:
    st.header("Acesso à API")
    api_key = st.text_input(
        "Google Gemini API Key",
        value=_load_default_api_key(),
        type="password",
        help="A chave é usada apenas durante esta execução. Não a publique nem a envie a terceiros.",
    )
    st.caption("Crie uma chave no Google AI Studio. O projeto usa a API Gemini.")

source = st.radio("Origem do documento", ["Enviar arquivo", "Colar texto"], horizontal=True)

full_text = ""
source_name = None
if source == "Enviar arquivo":
    uploaded = st.file_uploader("Envie o documento para análise (PDF ou DOCX)", type=list(SUPPORTED_EXTENSIONS))
    if uploaded:
        try:
            full_text = read_document(uploaded.getvalue(), uploaded.name)
        except Exception as exc:
            st.error(f"Erro ao ler o documento: {exc}")
            st.stop()
        if not full_text.strip():
            st.warning(
                "Não foi possível extrair texto. Este protótipo não faz OCR; "
                "use um PDF pesquisável, um DOCX ou cole o texto."
            )
            st.stop()
        source_name = uploaded.name
else:
    pasted = st.text_area(
        "Cole o texto do Entendimento do Objeto",
        height=320,
        placeholder="OBJETO DA AUDITORIA: ...\nOBJETIVO: ...\n\nContextualização\n...",
        help="Útil para documentos em outros formatos ou para analisar apenas parte de um documento.",
    )
    if pasted.strip():
        full_text = pasted.strip()
        source_name = "texto colado"

if source_name:
    st.success(f"Documento pronto: {len(full_text):,} caracteres serão enviados.")
    with st.expander("Prévia do texto enviado à IA"):
        st.text(full_text[:15000])

    if st.button("Executar os 3 experimentos", type="primary", disabled=not api_key.strip()):
        with st.spinner("Enviando o conteúdo para os três experimentos. Isso pode levar alguns minutos..."):
            try:
                results = run_experiments(full_text, api_key)
            except Exception as exc:
                st.error(f"Falha na análise: {exc}")
                st.stop()
            for result in results:
                if result.get("data"):
                    result["evidence_check"] = check_evidences(result["data"], full_text)
            st.session_state["results"] = results
            st.session_state["source_name"] = source_name

if "results" in st.session_state:
    results = st.session_state["results"]
    st.divider()
    st.subheader("Comparação dos experimentos")
    st.dataframe(compare_results(results), width="stretch", hide_index=True)
    st.caption(
        "**Evidências verificadas**: trechos citados pela IA que existem literalmente no documento "
        "(valores baixos indicam possível invenção)."
    )

    for result in results:
        with st.expander(f"{result['experiment']} — {result.get('model', '')}", expanded=True):
            if result.get("error"):
                st.error(result["error"])
                continue

            data = result["data"]
            generated = data["resultado_esperado_gerado"]

            tab_summary, tab_json = st.tabs(["Resumo", "Extração estruturada (JSON)"])
            with tab_summary:
                col_left, col_right = st.columns([3, 2])
                with col_left:
                    st.markdown("#### Resultados Esperados (gerado)")
                    st.write(generated["introducao"])
                    for item in generated["itens"]:
                        st.markdown(f"- **{item['texto']}**")
                        with st.popover("Fundamentação"):
                            st.write(item["fundamentacao"])
                            for ev in item["evidencias"]:
                                mark = "✅" if ev.get("verificada") else "⚠️ não encontrado no documento"
                                st.markdown(f"> {ev['trecho']}  \n_{ev['local']}_ — {mark}")

                    if data.get("resultado_esperado_original"):
                        st.markdown("#### Seção original encontrada no documento")
                        st.text(data["resultado_esperado_original"])

                with col_right:
                    st.markdown("#### Diagnóstico do documento")
                    for sec in data["diagnostico_secoes"]:
                        st.markdown(
                            f"{STATUS_ICON.get(sec['status'], '•')} **{sec['secao']}** — {sec['status']}  \n"
                            f"<small>{sec['observacao']}</small>",
                            unsafe_allow_html=True,
                        )

                st.markdown("#### Possíveis inconsistências")
                if data["inconsistencias"]:
                    for issue in data["inconsistencias"]:
                        st.warning(issue)
                else:
                    st.write("Nenhuma inconsistência explicitamente apontada pelo modelo.")

                if data["observacoes"]:
                    st.markdown("#### Observações")
                    for note in data["observacoes"]:
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

elif not source_name:
    st.info("Envie um documento ou cole o texto para começar.")
elif not api_key.strip():
    st.info("Informe sua chave API na barra lateral para habilitar a análise.")
