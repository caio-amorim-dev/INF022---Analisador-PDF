# Analisador de Documentos com IA

Aplicação Streamlit que:
1. Lê o papel de trabalho **Entendimento do Objeto** de uma auditoria: PDF pesquisável (com numeração das páginas), DOCX (com títulos e tabelas) ou texto colado.
2. Envia o documento inteiro à API Google Gemini, indicando quais seções pesam mais.
3. **Redige a seção Resultados Esperados**, com fundamentação e evidências literais para cada item.
4. Faz um diagnóstico das seções do documento (presente, parcial, só referência ou ausente) e aponta inconsistências.
5. Executa três experimentos com combinações diferentes de modelo e parâmetros e compara os resultados.
6. Confere automaticamente se cada trecho citado como evidência existe mesmo no documento.
7. Se o documento já tiver a seção Resultados Esperados, compara a versão gerada com a original em uma tabela lado a lado, indica o melhor de cada ponto, diz qual versão é melhor no geral e sugere uma versão consolidada.
8. Permite baixar os resultados em JSON.

## Requisitos

- Python 3.9 ou superior (recomendado 3.10+).
- Chave de API do Google Gemini (Free Tier ou pago).
- Conexão com a internet para chamar a API.

## Instalação

No terminal, dentro desta pasta:

```bash
python -m venv .venv
```

Ative o ambiente virtual:

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**Windows (Prompt de Comando):**
```bat
.venv\Scripts\activate.bat
```

**Linux/macOS:**
```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

## Executar

Opcionalmente, crie um arquivo `.env` a partir de `.env.example` para carregar a chave automaticamente:

```bash
cp .env.example .env
```

Preencha `GEMINI_API_KEY` no `.env` (ou informe a chave diretamente na barra lateral do app).

Com o ambiente virtual ativado, execute:

```bash
streamlit run main.py
```

Abra o endereço local mostrado pelo Streamlit (normalmente `http://localhost:8501`), confira/informe a chave Gemini na barra lateral e envie o documento (PDF ou DOCX) ou cole o texto. Na tela de resultados, cada experimento exibe as abas **Resumo** (Resultados Esperados gerados com fundamentação, diagnóstico das seções, possíveis inconsistências e observações) e **Extração estruturada (JSON)**.

## Estrutura

| Arquivo | Função |
|---|---|
| `main.py` | Interface Streamlit |
| `document_reader.py` | Leitura de PDF e DOCX |
| `prompt.py` | Instruções e prioridades de leitura do documento |
| `schemas.py` | Formato obrigatório da resposta (`response_schema` do Gemini) |
| `ai_processor.py` | Chamadas ao Gemini e execução dos experimentos |
| `evaluator.py` | Tabela comparativa e verificação das evidências |
| `config.py` | Modelos e parâmetros dos experimentos |

## Como o documento é lido

O documento inteiro é enviado, e o prompt indica o peso de cada parte:
- **Peso alto:** objeto, objetivo, contextualização, objetivos/indicadores/metas, descritivo do processo e riscos.
- **Peso médio:** marco regulatório, controle interno e metodologia.
- **Peso baixo (contexto):** participantes, aspecto organizacional, sistemas e contas contábeis.
- **Ignorado:** sumário, assinaturas, datas e links.

A resposta segue um formato fixo (`schemas.py`). Cada item do Resultado Esperado traz trechos copiados do documento como evidência, e o app confere se esses trechos existem de fato. A coluna **Evidências verificadas** da tabela mostra quantos foram encontrados; valores baixos indicam possível invenção do modelo.

## Comparação com a seção existente

Depois de redigir a sua versão, o modelo procura no documento uma seção de Resultados Esperados. Se encontrar, monta uma tabela:

| Gerado pela IA | Documento | Escolha | Justificativa |
|---|---|---|---|
| item semelhante | item semelhante | ✅ o melhor dos dois | … |
| item só da IA | — | ✅ Gerado ou ❌ Descartar | … |
| — | item só do documento | ✅ Documento ou ❌ Descartar | … |

Em seguida indica qual versão é **melhor no geral** e sugere uma **versão consolidada** com os pontos escolhidos.
Limitação: a comparação é feita pelo mesmo modelo que gerou o texto, que pode tender a favorecer a própria versão.

## Os três experimentos

As configurações ficam em `config.py` (modelos compatíveis com o Free Tier da API Gemini, cada um com cota independente por modelo):
- `gemini-3.1-flash-lite` — temperature 0.1, top-p 0.8.
- `gemini-3.6-flash` — temperature 0.5, top-p 0.9.
- `gemini-3.5-flash-lite` — temperature 0.2, top-p 0.8.

A disponibilidade dos modelos e dos parâmetros pode variar conforme a versão da API e a conta. Se uma configuração falhar, o erro aparecerá apenas naquele experimento. Verifique os modelos e parâmetros disponíveis na documentação atual do Gemini.

## Observações importantes

- Só o texto é enviado à IA; imagens são ignoradas. Não há OCR: PDFs que sejam apenas imagens precisam passar por OCR antes, ou o texto pode ser colado manualmente.
- O texto integral do documento é enviado à API. Considere confidencialidade, proteção de dados e políticas institucionais antes de usar documentos reais.
- Não coloque sua chave API no código-fonte, no Git ou em arquivos compartilhados.
- O Resultado Esperado gerado é uma **proposta** e deve ser revisado pelo auditor. As evidências servem para facilitar essa conferência.
- Documentos muito extensos podem exceder limites de contexto ou de requisição. Nesse caso, será necessário implementar divisão em blocos (chunking) e consolidação.
- A tabela comparativa é uma comparação simples (seções, itens e evidências), não uma avaliação automática de qualidade jurídica ou de auditoria.

## Personalização

Edite `prompt.py` para ajustar as instruções e prioridades e `schemas.py` para mudar o formato da resposta. Edite `config.py` para testar outros modelos e parâmetros.
