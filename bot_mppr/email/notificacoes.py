from database.database import obter_notificacoes_pendentes, registrar_notificacao
from .templates import montar_email
from .cliente import enviar_email
from bot_mppr.logger import logger


def enviar_notificacoes():

    notificacoes = obter_notificacoes_pendentes()
    logger.info("Envio de notificações")
    logger.info("=" * 60)
    if not notificacoes:
        logger.info("Nenhuma notificação pendente")
        return
    logger.info(
        "%s notificação(ões) pendente(s)",
        len(notificacoes)
    )
    assunto, corpo = montar_email(notificacoes)
    try:
        enviar_email(assunto, corpo)
        logger.info("=" * 60)
        logger.info("Registrando notificações")
        logger.info("=" * 60)
        for notificacao in notificacoes:
            registrar_notificacao(notificacao["ocorrencia_id"], "ENVIADO")
        logger.info(
            "%s notificação(ões) enviada(s)",
            len(notificacoes)
        )
    except Exception as erro:
        logger.exception(
            "Erro durante envio das notificações"
        )
        for notificacao in notificacoes:
            registrar_notificacao(notificacao["ocorrencia_id"], "ERRO", str(erro))
        raise