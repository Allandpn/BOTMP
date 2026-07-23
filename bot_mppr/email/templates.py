from datetime import datetime


def montar_email(notificacoes):

    cargos = set()
    linhas = []

    linhas.append("Boas Notícias!!!\n")
    linhas.append(
        "Foram encontradas novas movimentações relacionadas ao seu concurso "
        "de Técnico e Analista de Tecnologia da Informação do MPPR.\n"
    )

    linhas.append("=" * 60)

    for notificacao in notificacoes:
        linhas.append(
            f"\nEdição: {notificacao['numero']}/{notificacao['ano']} "
        )
        linhas.append(
            f"Página: {notificacao['pagina']}\n"
        )
        linhas.append(
            f"Diário Oficial: {notificacao['url']}\n"
        )
        linhas.append(
            notificacao["notificacao"].strip()
        )
        linhas.append("\n" + "=" * 60)
        cargos.add(notificacao["expressao"])

    linhas.append(
        f"\n\n\n\n\n\n\n\n\n\nGerado automaticamente pelo Bot MPPR em "
        f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
    )

    corpo = "\n".join(linhas)
    assunto = (
        f"Concurso MPPR - Nova notificação para o(s) cargo(s) de {", ".join(cargos)}"
    )

    return assunto, corpo




    