import logging
import os
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv


load_dotenv()

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_DIR = Path(__file__).parent / "logs"


def limpar_logs_antigos(dias=180):
    if not LOG_DIR.exists():
        return
    limite = datetime.now() - timedelta(days=dias)
    for arquivo in LOG_DIR.glob("*.log"):
        try:
            data_modificacao = datetime.fromtimestamp(arquivo.stat().st_mtime)
            if data_modificacao < limite:
                arquivo.unlink()
        except Exception:
            print(f"Não foi possível remover o log {arquivo}: {erro}")

def configurar_logger():
    LOG_DIR.mkdir(exist_ok=True)
    limpar_logs_antigos()
    logger = logging.getLogger("bot_mppr")
    logger.propagate = False
    if logger.handlers:
        return logger
    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))   
    nome_arquivo = datetime.now().strftime("%Y-%m-%d.log")
    arquivo_log = LOG_DIR / nome_arquivo     
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt = "%Y-%m-%d %H:%M:%S")
    file_handler = logging.FileHandler(arquivo_log, encoding="utf-8", delay=True)
    file_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

logger = configurar_logger()