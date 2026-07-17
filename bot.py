from scraper import buscar_novas_edicoes
from parser import processar_pdf


def main():

    print("Iniciando bot...")

    ultima_edicao = 1784  # depois vem do banco
    ultimo_ano = 2025     # depois vem do banco

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

    for edicao in novas_edicoes:

        numero = edicao["numero"]
        ano = edicao["ano"]
        pdf = edicao["pdf"]

        print("=" * 60)
        print(f"Processando edição {numero}/{ano}")
        print("=" * 60)

        ocorrencias = processar_pdf(pdf)

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


if __name__ == "__main__":
    main()