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


class AnaliseDocumento(BaseModel):
    objeto_da_auditoria: str
    objetivo: str
    diagnostico_secoes: list[DiagnosticoSecao]
    resultado_esperado_original: Optional[str] = Field(
        description="Texto da seção de Resultados Esperados já existente no documento, copiado literalmente; null se não existir."
    )
    resultado_esperado_gerado: ResultadoGerado
    inconsistencias: list[str] = Field(description="Contradições, desalinhamentos ou lacunas relevantes encontradas no documento.")
    observacoes: list[str] = Field(description="Limitações da análise e pontos que exigem validação humana.")
