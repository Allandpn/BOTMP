import json

from .cliente import enviar_prompt
from .prompts import PROMPT_ANALISTA


def classificar_ocorrencia(ocorrencia):
    prompt = f"""
    {PROMPT_ANALISTA}

    Cargo encontrado:
    {ocorrencia["expressao"]}

    Trecho:
    {ocorrencia["texto"]}
    """

    dados = enviar_prompt(prompt)

    return {
        "resultado": dados.resultado,
        "classificacao": dados.classificacao,
        "confianca": dados.confianca,
        "justificativa": dados.justificativa,        
        "notificacao": dados.notificacao,
        "modelo": "gemini-3.1-flash-lite"
    }


