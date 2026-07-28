from bot_mppr.scraper import buscar_novas_edicoes
from bot_mppr.parser import processar_pdf
from database.database import inicializar_banco, obter_estado, salvar_estado, salvar_edicao, marcar_edicao_processada, salvar_ocorencias, salvar_classificacao, obter_ocorrencias_sem_classificacao
from bot_mppr.ia.classificador_ia import classificar_ocorrencia
from bot_mppr.email.notificacoes import enviar_notificacoes
from bot_mppr.logger import logger


def main():

    logger.info("=" * 60)
    logger.info("Iniciando Bot MPPR")
    logger.info("=" * 60)

    inicializar_banco()

    estado = obter_estado()
    ultima_edicao = estado["ultima_edicao"]
    ultimo_ano = estado["ultimo_ano"]

    novas_edicoes = buscar_novas_edicoes(
        ultima_edicao,
        ultimo_ano
    )

    if not novas_edicoes:
        logger.info("Nenhuma edição nova encontrada.")
        return

    logger.info("%s nova(s) edição(ões) encontrada(s)", len(novas_edicoes))

    ultima_edicao_processada = None

    for edicao in novas_edicoes:

        numero = edicao["numero"]
        ano = edicao["ano"]
        pdf = edicao["pdf"]
        url = edicao["url"]

        edicao_id = salvar_edicao(
                    numero,
                    ano,
                    url
                )

        logger.info("=" * 60)
        logger.info("Processando edição %s/%s",numero, ano)
        logger.info("=" * 60)

        ocorrencias = processar_pdf(pdf)

        salvar_ocorencias(
            edicao_id,
            ocorrencias
        )

        marcar_edicao_processada(
                            edicao_id
                        )

        ultima_edicao_processada = edicao
        
        if not ocorrencias:
            logger.info("Nenhuma ocorrência encontrada na edição %s/%s", numero, ano)
            continue

        logger.info("%s ocorrência(s) encontrada(s) na edição %s/%s", len(ocorrencias), numero, ano)

    ocorrencias_sc = obter_ocorrencias_sem_classificacao()
    logger.info("=" * 60)
    logger.info("Salvar classificações IA no banco de dados")
    logger.info("=" * 60)
    for ocorrencia in ocorrencias_sc:
        try:
            resultado = classificar_ocorrencia(ocorrencia)
            salvar_classificacao(
                ocorrencia["id"], 
                resultado["resultado"], 
                resultado["classificacao"], 
                resultado["confianca"], 
                resultado["modelo"], 
                resultado["justificativa"],
                resultado["notificacao"]
                )
        except Exception as erro:
            logger.exception("Erro ao classificar ocorrencia %s", ocorrencia["id"])          

    if ultima_edicao_processada:
        salvar_estado(ultima_edicao_processada["numero"], ultima_edicao_processada["ano"])
    
    enviar_notificacoes()
    logger.info("=" * 60)
    logger.info("Execução finalizada com sucesso.")
    logger.info("=" * 60)   


if __name__ == "__main__":
    main()


