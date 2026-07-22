from pydantic import BaseModel

class ClassificacaoIA(BaseModel):
    resultado: str
    classificacao: str
    confianca: float
    justificativa: str
    notificacao: str