# Analisador de PDF com IA

Aplicação Streamlit que:
1. Lê o texto de um PDF pesquisável, preservando a numeração das páginas.
2. Envia o conteúdo à API Google Gemini.
3. Executa três experimentos com combinações diferentes de modelo e parâmetros.
4. Extrai atributos documentais, evidências, inconsistências e a seção **Resultado Esperado**.
5. Permite baixar os resultados em JSON.

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

Abra o endereço local mostrado pelo Streamlit (normalmente `http://localhost:8501`), confira/informe a chave Gemini na barra lateral e envie o PDF. Na tela de resultados, cada experimento exibe as abas **Resumo** (Resultado Esperado, possíveis inconsistências e observações) e **Extração estruturada (JSON)**.

## Os três experimentos

As configurações ficam em `config.py` (modelos compatíveis com o Free Tier da API Gemini, cada um com cota independente por modelo):
- `gemini-3.1-flash-lite` — temperature 0.1, top-p 0.8.
- `gemini-3.6-flash` — temperature 0.5, top-p 0.9.
- `gemini-3.5-flash-lite` — temperature 0.2, top-p 0.8.

A disponibilidade dos modelos e dos parâmetros pode variar conforme a versão da API e a conta. Se uma configuração falhar, o erro aparecerá apenas naquele experimento. Verifique os modelos e parâmetros disponíveis na documentação atual do Gemini.

## Observações importantes

- Este protótipo extrai texto com PyMuPDF; não possui OCR. PDFs que sejam apenas imagens precisam passar por OCR antes.
- O texto integral do PDF é enviado à API. Considere confidencialidade, proteção de dados e políticas institucionais antes de usar documentos reais.
- Não coloque sua chave API no código-fonte, no Git ou em arquivos compartilhados.
- As respostas de IA devem ser revisadas por uma pessoa. As evidências e páginas servem para facilitar essa conferência.
- PDFs muito extensos podem exceder limites de contexto ou de requisição. Nesse caso, será necessário implementar divisão em blocos (chunking) e consolidação.
- A contagem de atributos é uma comparação simples de status, não uma avaliação automática de qualidade jurídica ou de auditoria.

## Personalização

Edite `prompt.py` para ajustar os atributos e critérios. Edite `config.py` para testar outros modelos e parâmetros.
