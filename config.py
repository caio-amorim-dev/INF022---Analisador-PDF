# Modelos compatíveis com o Free Tier da API Gemini e parâmetros de geração.
# Se a API/modelo não aceitar algum parâmetro, a chamada retornará um erro
# que será exibido no resultado daquele experimento.
EXPERIMENTS = [
    {
        "name": "Experimento 1 — Flash Lite (extração conservadora)",
        "model": "gemini-3.1-flash-lite",
        "temperature": 0.1,
        "top_p": 0.8,
    },
    {
        "name": "Experimento 2 — Flash 3.6 (síntese moderada)",
        "model": "gemini-3.6-flash",
        "temperature": 0.5,
        "top_p": 0.9,
    },
    {
        "name": "Experimento 3 — Flash Lite 3.5 (análise principal)",
        "model": "gemini-3.5-flash-lite",
        "temperature": 0.2,
        "top_p": 0.8,
    },
]
