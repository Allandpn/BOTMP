from bot_mppr.scraper import buscar_novas_edicoes
from bot_mppr.parser import processar_pdf
from database.database import inicializar_banco, obter_estado, salvar_estado, salvar_edicao, marcar_edicao_processada, salvar_ocorencias, salvar_classificacao, obter_ocorrencias_sem_classificacao
from bot_mppr.ia.classificador_ia import classificar_ocorrencia
from bot_mppr.email.notificacoes import enviar_notificacoes


def main():

    print("Iniciando bot...")

    inicializar_banco()

    estado = obter_estado()
    ultima_edicao = estado["ultima_edicao"]
    ultimo_ano = estado["ultimo_ano"]

    novas_edicoes = buscar_novas_edicoes(
        ultima_edicao,
        ultimo_ano
    )

    if not novas_edicoes:
        print("Nenhuma nova edição encontrada.")
        return

    print(
        f"{len(novas_edicoes)} nova(s) edição(ões) encontrada(s)"
    )

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

        print("=" * 60)
        print(f"Processando edição {numero}/{ano}")
        print("=" * 60)       

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
            print(
                f"Nenhuma ocorrência encontrada "
                f"na edição {numero}/{ano}"
            )
            continue

        print(
            f"{len(ocorrencias)} ocorrência(s) "
            f"encontrada(s) na edição {numero}/{ano}"
        )  
        for ocorrencia in ocorrencias:
            print(ocorrencia)

    ocorrencias_sc = obter_ocorrencias_sem_classificacao()
       
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
            print(f"Erro ao classificar ocorrencia {ocorrencia["id"]}: {erro}")         
        

    if ultima_edicao_processada:
        salvar_estado(ultima_edicao_processada["numero"], ultima_edicao_processada["ano"])

    enviar_notificacoes()   


if __name__ == "__main__":
    main()


