import re
import unicodedata
import pdfplumber
import fitz  
from collections import defaultdict


# ==============================
# CONFIG
# ==============================

EXPRESSOES_ALVO = [
    {
        "nome": "Analista de Tecnologia da Informação",

        "variacoes": [
            "ANALISTA TEC INFORMACAO",
            "ANALISTA DE TECNOLOGIA DA INFORMACAO",
            "ANALISTA TECNOL. INFORMACAO",
            "ANALISTA TECNOL. INFORMAÇÃO"
        ],

        "termos": [
            "ANALISTA",
            "TEC",
            "INFORMA"
        ]
    },

    {
        "nome": "Técnico de Tecnologia da Informação",

        "variacoes": [
            "TECNICO TEC DA INFORMACAO",
            "TECNICO DE TECNOLOGIA DA INFORMACAO",
            "TECNICO TECNOL. INFORMACAO",
            "TECNICO TECNOL. INFORMAÇÃO"
        ],

        "termos": [
            "TECNICO",
            "TEC",
            "INFORMA"
        ]
    }
]
TAMANHO_CONTEXTO = 330
DISTANCIA_MAXIMA_TERMOS = 100


# ==============================
# 1. EXTRAÇÃO COM COLUNAS
# ==============================


def extrair_texto_estruturado(pdf_file):
   
    paginas = []

    pdf_file.seek(0)

    documento = fitz.open(
        stream=pdf_file.read(),
        filetype="pdf"
    )

    try:
        for numero_pagina, pagina in enumerate(documento, start=1):

            palavras = pagina.get_text(
                "words",
                sort=True
            )

            linhas = defaultdict(list)

            for palavra in palavras:

                x0, y0, x1, y1, texto, bloco, linha, numero = palavra

                chave = (bloco, linha)

                linhas[chave].append((x0, texto))

            texto_final = []

            for chave in sorted(linhas):

                palavras_linha = sorted(linhas[chave])

                linha = " ".join(
                    texto
                    for _, texto in palavras_linha
                )

                texto_final.append(linha)

            paginas.append({
                "pagina": numero_pagina,
                "texto": "\n".join(texto_final)
            })

    finally:
        documento.close()
        pdf_file.seek(0)

    return paginas


def extrair_texto_estruturado3(pdf_file):
    """
    Extrai o texto utilizando os blocos do PyMuPDF.
    """

    paginas = []

    pdf_file.seek(0)

    documento = fitz.open(
        stream=pdf_file.read(),
        filetype="pdf"
    )

    try:
        for numero_pagina, pagina in enumerate(documento, start=1):

            blocos = pagina.get_text(
                "blocks",
                sort=True
            )

            linhas = []

            for bloco in blocos:

                texto = bloco[4].strip()

                if texto:
                    linhas.append(texto)

            paginas.append({
                "pagina": numero_pagina,
                "texto": "\n".join(linhas)
            })

    finally:
        documento.close()
        pdf_file.seek(0)

    return paginas


def extrair_texto_estruturado2(pdf_file):

    paginas = []

    with pdfplumber.open(pdf_file) as pdf:

        for numero_pagina, pagina in enumerate(pdf.pages, start=1):

            largura = pagina.width
            meio = largura / 2

            esquerda = pagina.crop(
                (0, 0, meio, pagina.height)
            )

            direita = pagina.crop(
                (meio, 0, largura, pagina.height)
            )

            texto_esq = esquerda.extract_text()
            texto_dir = direita.extract_text()

            # Página com 2 colunas
            if texto_esq and texto_dir:

                texto = (
                    texto_esq
                    + "\n"
                    + texto_dir
                )

            else:

                texto = pagina.extract_text() or ""

            paginas.append({
                "pagina": numero_pagina,
                "texto": texto
            })

    return paginas


# ==============================
# 2. NORMALIZAÇÃO
# ==============================

def normalizar_texto(texto):

    if not texto:
        return ""

    # Remove acentos
    texto = unicodedata.normalize(
        "NFD",
        texto
    )

    texto = "".join(
        caractere
        for caractere in texto
        if unicodedata.category(caractere) != "Mn"
    )

    # Converte para maiúsculas
    texto = texto.upper()

    # Substitui quebras de linha, tabs e
    # múltiplos espaços por um único espaço
    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto.strip()


# ==============================
# 3. BUSCAR EXPRESSÃO
# ==============================

def buscar_expressoes(paginas):
    
    with open("debug_extracao.txt","w",encoding="utf-8") as arquivo_debug:

        resultados = []

        for pagina in paginas:

            numero_pagina = pagina["pagina"]        
            
            texto = normalizar_texto(
                pagina["texto"]
            )
            
            salvar_texto(pagina, texto, arquivo_debug)

            for expressao in EXPRESSOES_ALVO:

                nome = expressao["nome"]

                intervalos_exatos = []

                # ==============================
                # 1. BUSCAS EXATAS
                # ==============================

                for variacao in expressao["variacoes"]:

                    alvo = normalizar_texto(
                        variacao
                    )

                    for match in re.finditer(
                        re.escape(alvo),
                        texto
                    ):

                        # Evita que duas variações exatas
                        # capturem a mesma ocorrência
                        duplicado = any(
                            match.start() < fim_existente
                            and match.end() > inicio_existente
                            for inicio_existente, fim_existente
                            in intervalos_exatos
                        )

                        if duplicado:
                            continue

                        intervalos_exatos.append(
                            (
                                match.start(),
                                match.end()
                            )
                        )

                        inicio = max(
                            0,
                            match.start() - TAMANHO_CONTEXTO
                        )

                        fim = min(
                            len(texto),
                            match.end() + TAMANHO_CONTEXTO
                        )

                        contexto = texto[
                            inicio:fim
                        ]

                        resultados.append({
                            "pagina": numero_pagina,
                            "expressao": nome,
                            "tipo_busca": "exata",
                            "texto": contexto
                        })

                # ==============================
                # 2. BUSCA FLEXÍVEL
                # ==============================

                padrao = criar_padrao_flexivel(
                    expressao["termos"]
                )

                for match in re.finditer(
                    padrao,
                    texto
                ):

                    # Ignora se a busca flexível
                    # capturou uma ocorrência já
                    # encontrada pela busca exata
                    sobrepoe_exata = any(
                        match.start() < fim_exato
                        and match.end() > inicio_exato
                        for inicio_exato, fim_exato
                        in intervalos_exatos
                    )

                    if sobrepoe_exata:
                        continue

                    inicio = max(
                        0,
                        match.start() - TAMANHO_CONTEXTO
                    )

                    fim = min(
                        len(texto),
                        match.end() + TAMANHO_CONTEXTO
                    )

                    contexto = texto[
                        inicio:fim
                    ]

                    resultados.append({
                        "pagina": numero_pagina,
                        "expressao": nome,
                        "tipo_busca": "flexivel",
                        "texto": contexto
                    })

    return resultados


def criar_padrao_flexivel(termos):
    termos_normalizados = [normalizar_texto(termo) for termo in termos]
    
    separador = rf".{{0,{DISTANCIA_MAXIMA_TERMOS}}}?"
    
    return separador.join(re.escape(termo) for termo in termos_normalizados)
    

# ==============================
# PIPELINE COMPLETO
# ==============================

def processar_pdf(pdf_file):

    paginas = extrair_texto_estruturado(
        pdf_file
    )

    resultados = buscar_expressoes(
        paginas
    )

    return resultados


def salvar_texto(pagina, texto_normalizado, arquivo_debug):

    # Salva o texto no arquivo
    arquivo_debug.write(
        f"\n{'=' * 80}\n"
    )
    arquivo_debug.write(
        f"PÁGINA {pagina["pagina"]}\n"
    )
    arquivo_debug.write(
        f"{'=' * 80}\n\n"
    )

    arquivo_debug.write(
        "=== TEXTO ORIGINAL ===\n\n"
    )
    arquivo_debug.write(
        pagina["texto"]
    )

    arquivo_debug.write(
        "\n\n=== TEXTO NORMALIZADO ===\n\n"
    )
    arquivo_debug.write(
        texto_normalizado
    )

    arquivo_debug.write(
        "\n\n"
    )