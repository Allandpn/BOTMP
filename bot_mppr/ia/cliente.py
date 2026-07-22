import os

from dotenv import load_dotenv
from google import genai
from .modelos import ClassificacaoIA

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY não configurada.")

cliente = genai.Client(api_key=API_KEY)

def enviar_prompt(prompt):
    resposta = cliente.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": ClassificacaoIA
        }
    )
    return resposta.parsed