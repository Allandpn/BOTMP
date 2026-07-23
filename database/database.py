import sqlite3
from pathlib import Path
from datetime import datetime
import json


DATABASE_DIR = Path(__file__).parent

DATABASE_PATH = DATABASE_DIR / "bot.db"

SCHEMA_PATH = DATABASE_DIR / "schema.sql"


def conectar_banco():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def inicializar_banco():
    with conectar_banco() as conn:
        with open(
            SCHEMA_PATH,
            "r",
            encoding="utf-8"
        ) as arquivo:
            conn.executescript(
                arquivo.read()
            )
        conn.execute(
            """
            INSERT OR IGNORE INTO estado
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


def obter_estado():
    conn = conectar_banco()
    try:
        estado = conn.execute(
            """
            SELECT 
                ultima_edicao,
                ultimo_ano
            FROM estado
            WHERE id = 1
            """
        ).fetchone()

        return {
            "ultima_edicao": estado["ultima_edicao"],
            "ultimo_ano": estado["ultimo_ano"]
        }
    finally:
        conn.close()

        
def salvar_estado(ultima_edicao, ultimo_ano):
    conn = conectar_banco()
    try:
        conn.execute(
            """
            UPDATE estado
            SET
                ultima_edicao = ?,
                ultimo_ano = ?,
                ultima_atualizacao = ?
            WHERE id = 1
            """,
            (
                ultima_edicao,
                ultimo_ano,
                datetime.now().isoformat()
            )
        )
        conn.commit()
    finally:
        conn.close()


def salvar_edicao(numero, ano, url):
    conn = conectar_banco()
    try:
        cursor = conn.execute(
            """
            INSERT OR IGNORE INTO edicoes
            (
                numero,
                ano,
                url,
                data_download,
                processada
            )
            VALUES
            (
                ?, ?, ?, ?, 0
            )
            """,
            (
                numero,
                ano,
                url,
                datetime.now().isoformat()
            )
        )
        conn.commit()
        edicao = conn.execute(
            """
            SELECT id
            FROM edicoes
            WHERE numero = ?
            AND ano = ?
            """,
            (
                numero,
                ano
            )
        ).fetchone()
        return edicao["id"]
    finally:
        conn.close()


def marcar_edicao_processada(edicao_id):
    conn = conectar_banco()
    try:
        conn.execute(
            """
            UPDATE edicoes
            SET processada = 1
            WHERE id = ?
            """,
            (edicao_id,)
        )
        conn.commit()
    finally:
        conn.close()


def salvar_ocorencias(edicao_id, ocorrencias):
    conn = conectar_banco()
    try:
        for ocorrencia in ocorrencias:
            conn.execute(
                """
                INSERT INTO ocorrencias
                (
                    edicao_id,
                    pagina,
                    expressao,
                    tipo_busca,
                    texto,
                    data_encontrada
                )
                VALUES
                (
                    ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    edicao_id,
                    ocorrencia["pagina"],
                    ocorrencia["expressao"],
                    ocorrencia["tipo_busca"],
                    ocorrencia["texto"],
                    datetime.now().isoformat()
                )
            )
        conn.commit()
    finally:
        conn.close()


def obter_ocorrencias_sem_classificacao():
    conn = conectar_banco()
    try:
        ocorrencias = conn.execute(
            """
            SELECT o.*
            FROM ocorrencias o
            LEFT JOIN classificacoes_ia c
            ON c.ocorrencia_id = o.id
            WHERE c.id IS NULL
            ORDER BY o.id
            """
        ).fetchall()
        return [dict(ocorrencia) for ocorrencia in ocorrencias]
    finally:
        conn.close()



def salvar_classificacao(ocorrencia_id, resultado, classificacao, confianca, modelo, justificativa, notificacao):
    conn = conectar_banco()
    try:
        conn.execute(
            """
            INSERT INTO classificacoes_ia
            (
                ocorrencia_id,
                resultado,
                classificacao,
                confianca,
                modelo,
                justificativa,
                data_classificacao,
                notificacao
            )
            VALUES
            (
                ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                ocorrencia_id,
                resultado,
                classificacao,
                confianca,
                modelo,
                justificativa,
                datetime.now().isoformat(),
                notificacao
            )
        )
        conn.commit()
    finally:
        conn.close()


def obter_notificacoes_pendentes():
    conn = conectar_banco()
    try:
        notificacoes = conn.execute(
        """
            SELECT
            o.id AS ocorrencia_id,
            e.numero,
            e.ano,
            o.pagina,            
            e.url,            
            o.expressao,
            c.classificacao,
            c.notificacao
            FROM classificacoes_ia c
            INNER JOIN ocorrencias o
            ON o.id = c.ocorrencia_id
            INNER JOIN edicoes e
            ON e.id = o.edicao_id
            LEFT JOIN notificacoes n
            ON n.ocorrencia_id = o.id
            AND n.canal = 'EMAIL'
            AND n.status = 'ENVIADO'
            WHERE c.resultado = 'RELEVANTE'
            AND n.id IS NULL
            ORDER BY e.ano, e.numero, o.pagina;
        """
        ).fetchall()
        return [dict(item) for item in notificacoes]
    finally:
        conn.close()


def registrar_notificacao(ocorrencia_id, status, erro=None):
    conn = conectar_banco()
    try:
        conn.execute(
        """
            INSERT INTO notificacoes
            (
                ocorrencia_id,
                canal,
                status, 
                tentativas,
                data_envio,
                erro
            )
            VALUES
            (
                ?,?,?,?,?,?
            )
        """,
            (
                ocorrencia_id,
                "EMAIL",
                status,
                1,
                datetime.now().isoformat(),
                erro
            )
        )
        conn.commit()
    finally:
        conn.close()


# result = obter_notificacoes_pendentes()
# print(json.dumps(result, indent=4, ensure_ascii=False))