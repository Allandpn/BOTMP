from database.database import obter_notificacoes_pendentes, registrar_notificacao
from .templates import montar_email
from .cliente import enviar_email


def enviar_notificacoes():

    notificacoes = obter_notificacoes_pendentes()

    if not notificacoes:
        print("Nenhuma notificacao pendente.")
        return

    assunto, corpo = montar_email(notificacoes)

    try:
        enviar_email(assunto, corpo)
        for notificacao in notificacoes:
            registrar_notificacao(notificacao["ocorrencia_id"], "ENVIADO")
        print(f"{len(notificacoes)} notificações enviadas.")
    except Exception as erro:
        for notificacao in notificacoes:
            registrar_notificacao(notificacao["ocorrencia_id"], "ERRO", erro)
        raise