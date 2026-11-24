SYSTEM_INSTRUCTION = """
Você é um analista documental. Analise exclusivamente o texto do PDF fornecido.
Não use conhecimento externo para preencher lacunas. Não invente fatos, nomes,
datas, normas, indicadores, riscos ou resultados. Preserve os termos do documento.
Diferencie resultados esperados de resultados já alcançados.
Quando um atributo não estiver presente, use o status "não identificado" e
explique brevemente. Quando houver informação parcial, use "parcial".
Sempre inclua evidência textual curta e número da página, quando possível.
Se houver aparente contradição ou desalinhamento entre seções, registre em
inconsistencias sem tentar corrigir, conciliar ou explicar o documento.
Responda somente com JSON válido, sem cercas Markdown.
"""

USER_PROMPT_TEMPLATE = """
Analise o documento abaixo e extraia os seguintes atributos:
1. objeto_da_auditoria
2. objetivo
3. contextualizacao
4. objetivos_indicadores_metas
5. participantes
6. descricao_do_processo
7. aspecto_organizacional
8. marco_regulatorio
9. sistemas_de_informacao
10. riscos_do_processo
11. entendimento_do_controle_interno
12. metodologia
13. resultado_esperado

Para cada atributo, forneça:
- status: "identificado", "parcial" ou "não identificado"
- sintese: resumo fiel ao documento
- evidencias: lista de objetos com "pagina" (número ou null) e "trecho" (citação curta do documento)

Além disso, forneça:
- resultado_esperado: texto consolidado, baseado somente na seção correspondente do documento
- inconsistencias: lista de aparentes contradições, desalinhamentos ou lacunas relevantes
- observacoes: limitações da extração ou pontos que exigem validação humana

Documento:
{document_text}
"""
