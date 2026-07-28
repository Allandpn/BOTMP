import os
import smtplib
from bot_mppr.logger import logger
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_DESTINO = os.getenv("EMAIL_DESTINO")

def enviar_email(assunto, corpo):

    msg = EmailMessage()

    msg["Subject"] = assunto
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_DESTINO
    msg.set_content(corpo)
    logger.info(
        "Conectando ao servidor SMTP %s:%s",
        EMAIL_HOST,
        EMAIL_PORT
    )
    try: 
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(EMAIL_USER, EMAIL_PASSWORD)
            logger.info(
                "Enviando e-mail para %s",
                EMAIL_DESTINO
            )
            smtp.send_message(msg)
            logger.info("E-mail enviado com sucesso")
    except Exception:
        logger.exception("Erro ao enviar e-mail")
        raise


