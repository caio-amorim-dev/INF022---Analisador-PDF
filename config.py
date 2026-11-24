# Modelos e parâmetros de geração usados nos três experimentos.
# Se a API/modelo não aceitar algum parâmetro, a chamada retornará um erro
# que será exibido no resultado daquele experimento.
EXPERIMENTS = [
    {
        "name": "Experimento 1 — extração conservadora",
        "model": "gemini-2.5-flash",
        "temperature": 0.1,
        "top_p": 0.8,
        "top_k": 20,
    },
    {
        "name": "Experimento 2 — síntese moderada",
        "model": "gemini-2.5-flash",
        "temperature": 0.5,
        "top_p": 0.9,
        "top_k": 40,
    },
    {
        "name": "Experimento 3 — modelo Pro",
        "model": "gemini-2.5-pro",
        "temperature": 0.2,
        "top_p": 0.8,
        "top_k": 20,
    },
]
