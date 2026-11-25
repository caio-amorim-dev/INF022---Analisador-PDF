"""Estrutura de resposta enviada ao Gemini como response_schema.

O schema obriga o modelo a devolver sempre o mesmo formato, o que elimina
o "adivinhar" de chaves na hora de exibir e comparar os experimentos.
"""
from typing import Literal, Optional

from pydantic import BaseModel, Field

# Seções do modelo de "Entendimento do Objeto" usado pela auditoria.
SECOES_MODELO = [
    "Objeto da auditoria",
    "Objetivo",
    "Contextualização",
    "Objetivos, indicadores e metas",
    "Participantes",
    "Descritivo do processo",
    "Aspecto organizacional",
    "Marco regulatório",
    "Sistemas de informação",
    "Riscos do processo",
    "Entendimento do controle interno",
    "Contas contábeis / Materialidade",
    "Metodologia",
    "Resultados esperados",
]

StatusSecao = Literal["presente", "parcial", "apenas referência", "ausente"]


class Evidencia(BaseModel):
    local: str = Field(description='Onde está o trecho: "página N" (PDF) ou o nome da seção.')
    trecho: str = Field(description="Cópia literal e curta (até ~30 palavras) do texto do documento.")


class DiagnosticoSecao(BaseModel):
    secao: str = Field(description="Nome da seção, exatamente como na lista de seções do modelo.")
    status: StatusSecao
    observacao: str = Field(description="Uma frase justificando o status.")


class ItemResultado(BaseModel):
    texto: str = Field(description="O item do resultado esperado, iniciado por verbo no infinitivo.")
    fundamentacao: str = Field(description="Por que este resultado é esperado, ligando-o ao objetivo, risco ou contexto do documento.")
    evidencias: list[Evidencia]


class ResultadoGerado(BaseModel):
    introducao: str = Field(description='Frase de abertura, por exemplo "Espera-se, ao final da auditoria:".')
    itens: list[ItemResultado]


EscolhaComparacao = Literal["gerado", "documento", "descartar"]


class LinhaComparacao(BaseModel):
    item_gerado: Optional[str] = Field(
        description="Item da versão gerada; null se o ponto só existe na versão do documento."
    )
    item_documento: Optional[str] = Field(
        description="Item da seção original do documento; null se o ponto só existe na versão gerada."
    )
    escolha: EscolhaComparacao = Field(
        description=(
            'Pontos semelhantes (os dois preenchidos): "gerado" ou "documento", conforme o melhor. '
            'Ponto só de um lado: o nome desse lado se vale a pena incluir, ou "descartar".'
        )
    )
    justificativa: str = Field(description="Uma frase explicando a escolha.")


class ComparacaoResultados(BaseModel):
    linhas: list[LinhaComparacao] = Field(
        description="Uma linha por ponto. Itens semelhantes das duas versões ficam na mesma linha."
    )
    melhor_no_geral: Literal["gerado", "documento", "equivalentes"]
    justificativa_geral: str
    versao_consolidada: list[str] = Field(
        description="Lista final com os itens escolhidos (de qualquer das duas versões), na ordem recomendada."
    )


class AnaliseDocumento(BaseModel):
    objeto_da_auditoria: str
    objetivo: str
    diagnostico_secoes: list[DiagnosticoSecao]
    resultado_esperado_original: Optional[str] = Field(
        description="Texto da seção de Resultados Esperados já existente no documento, copiado literalmente; null se não existir."
    )
    resultado_esperado_gerado: ResultadoGerado
    comparacao: Optional[ComparacaoResultados] = Field(
        description="Comparação entre a versão gerada e a seção original; null se o documento não tiver a seção."
    )
    inconsistencias: list[str] = Field(description="Contradições, desalinhamentos ou lacunas relevantes encontradas no documento.")
    observacoes: list[str] = Field(description="Limitações da análise e pontos que exigem validação humana.")
