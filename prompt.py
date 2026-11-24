from schemas import SECOES_MODELO

SYSTEM_INSTRUCTION = """
Você é um auditor interno do setor público que apoia a elaboração do papel de
trabalho "Entendimento do Objeto" na fase de planejamento de uma auditoria.

Sua tarefa principal é REDIGIR a seção "Resultados Esperados" da auditoria a
partir do documento fornecido. Na maioria dos casos essa seção ainda não existe
no documento: você deve produzi-la. Se ela já existir, copie-a em
resultado_esperado_original e, mesmo assim, redija a sua versão.

Regras de fundamentação:
- Use somente o conteúdo do documento. Não use conhecimento externo para
  acrescentar normas, números, unidades, sistemas ou fatos que não estejam nele.
- Cada item do resultado esperado deve decorrer do objetivo da auditoria e ser
  sustentado por pelo menos uma evidência do documento.
- Em "evidencias.trecho", copie o texto literalmente, sem parafrasear, pois os
  trechos serão conferidos automaticamente contra o documento.
- Resultados esperados descrevem o que a auditoria pretende entregar ou
  contribuir (avaliar, identificar, propor, contribuir para...). Não afirme
  achados, conclusões ou irregularidades, pois a auditoria ainda não foi feita.
- Se o documento for pobre em conteúdo, gere menos itens e registre a limitação
  em observacoes, em vez de preencher com generalidades.
- Registre contradições ou desalinhamentos entre seções em inconsistencias,
  sem tentar corrigi-los.
""".strip()

_PRIORIDADES = """
Como ler o documento (analise o documento inteiro, com esta ordem de peso):

PESO ALTO — definem o que a auditoria vai entregar:
- Objeto da auditoria e Objetivo (o resultado esperado deve responder a eles);
- Contextualização (motivação, riscos e problemas citados);
- Objetivos, indicadores e metas (metas e indicadores que a auditoria pode apoiar);
- Descritivo do processo (etapas que serão avaliadas);
- Riscos do processo (quando houver conteúdo, não apenas referência a outro papel de trabalho).

PESO MÉDIO — critérios e forma da avaliação:
- Marco regulatório (normas que servem de critério de conformidade);
- Entendimento do controle interno e Metodologia.

PESO BAIXO — use apenas como contexto:
- Participantes, Aspecto organizacional (transcrições de competências),
  Sistemas de informação, Contas contábeis / Materialidade.

IGNORE: sumário, assinaturas ("Elaborado por", "Revisado por"), datas de
elaboração, links e referências a apêndices ou fluxogramas não incluídos.
""".strip()

_FORMATO = """
Formato do resultado esperado gerado:
- introducao: "Espera-se, ao final da auditoria:";
- de 4 a 7 itens, cada um uma frase curta iniciada por verbo no infinitivo;
- os itens devem ser específicos ao objeto auditado (cite o tema, o processo
  ou a norma do documento), evitando frases que serviriam para qualquer auditoria.
""".strip()


def build_user_prompt(document_text: str) -> str:
    secoes = "\n".join(f"- {s}" for s in SECOES_MODELO)
    partes = [
        _PRIORIDADES,
        _FORMATO,
        "Em diagnostico_secoes, informe uma entrada para cada seção do modelo abaixo, "
        'com status "presente", "parcial", "apenas referência" (quando a seção só '
        'aponta para outro papel de trabalho) ou "ausente":\n' + secoes,
        f"Documento:\n<<<\n{document_text}\n>>>",
    ]
    return "\n\n".join(partes)
