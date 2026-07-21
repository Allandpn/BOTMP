import sqlite3
from pathlib import Path
from datetime import datetime


DATABASE_DIR = Path(__file__).parent

DATABASE_PATH = DATABASE_DIR / "bot.db"

SCHEMA_PATH = DATABASE_DIR / "schema.sql"


def conectar():
    
    print(SCHEMA_PATH)

    conn = sqlite3.connect(DATABASE_PATH)

    conn.row_factory = sqlite3.Row

    conn.execute("PRAGMA foreign_keys = ON")

    return conn


def inicializar_banco():

    with conectar() as conn:

        with open(
            SCHEMA_PATH,
            "r",
            encoding="utf-8"
        ) as arquivo:

            conn.executescript(
                arquivo.read()
            )

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM estado
            """
        )

        if cursor.fetchone()[0] == 0:

            cursor.execute(
                """
                INSERT INTO estado
                (
                    id,
                    ultima_edicao,
                    ultimo_ano,
                    ultima_atualizacao
                )
                VALUES
                (
                    1,
                    0,
                    2025,
                    ?
                )
                """,
                (
                    datetime.now().isoformat(),
                )
            )

        conn.commit()
        
inicializar_banco()