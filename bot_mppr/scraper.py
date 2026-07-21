import requests
from io import BytesIO
from datetime import datetime

BASE_URL = (
    "https://apps.mppr.mp.br/"
    "bdoc/solr-1.0-SNAPSHOT/"
    "solrServices/br.mp.mppr.solr.download/"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)

TIMEOUT = 30

MAX_FALHAS_CONSECUTIVAS = 3


def gerar_url(edicao, ano):

    numero = f"{edicao:06d}"

    nome = f"DEMPPR{numero}{ano}.pdf"

    return (
        f"{BASE_URL}"
        f"?nomearquivo={nome}"
        f"&dir=%2Fvar%2Fdiario%2F"
    )


def baixar_pdf(edicao, ano):

    url = gerar_url(edicao, ano)

    try:

        response = SESSION.get(
            url,
            timeout=TIMEOUT
        )

        if response.status_code == 404:
            return None
        
        if not response.content.startswith(b"%PDF"):
            return None

        return {
            "numero": edicao,
            "ano": ano,
            "url": url,
            "pdf": BytesIO(response.content)
        }

    except requests.RequestException as erro:
        if response is not None:
            print(
                f"Erro HTTP {response.status_code} ao baixar {edicao}/{ano}"
            )
        else:
            print(f"Erro {erro} ao baixar {edicao}/{ano}")

        return None


def buscar_novas_edicoes(
    ultima_edicao,
    ultimo_ano
):

    novas_edicoes = []

    edicao_atual = ultima_edicao + 1
    ano_atual = ultimo_ano
    ano_corrente = datetime.now().year

    falhas_consecutivas = 0

    while (
        falhas_consecutivas
        < MAX_FALHAS_CONSECUTIVAS
    ):

        print(
            f"Verificando edição "
            f"{edicao_atual}/{ano_atual}..."
        )

        # ===================================
        # Primeiro tenta no ano atual
        # ===================================

        edicao = baixar_pdf(
            edicao_atual,
            ano_atual
        )

        # ===================================
        # Tenta ano seguinte, se permitido
        # ===================================

        if (
            edicao is None
            and ano_atual < ano_corrente
        ):

            proximo_ano = ano_atual + 1

            print(
                f"Tentando "
                f"{edicao_atual}/{proximo_ano}..."
            )

            edicao = baixar_pdf(
                edicao_atual,
                proximo_ano
            )

            if edicao:

                ano_atual = proximo_ano

                print(
                    f"Mudança de ano detectada: "
                    f"{ano_atual}"
                )

        # ===================================
        # Resultado
        # ===================================

        if edicao:

            print(
                f"Edição "
                f"{edicao['numero']}/"
                f"{edicao['ano']} encontrada."
            )

            novas_edicoes.append(
                edicao
            )

            falhas_consecutivas = 0

        else:

            print(
                f"Edição "
                f"{edicao_atual} não encontrada."
            )

            falhas_consecutivas += 1

        edicao_atual += 1

    return novas_edicoes