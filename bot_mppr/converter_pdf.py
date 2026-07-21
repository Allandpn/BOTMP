import pdfplumber
import os

INPUT_PDF = "pdf/diario.pdf"
OUTPUT_TXT = "output/diario.txt"


def extrair_texto_corrigido(pdf_path):

    texto_final = ""

    with pdfplumber.open(pdf_path) as pdf:

        for i, pagina in enumerate(pdf.pages):

            largura = pagina.width
            altura = pagina.height

            meio = largura / 2

            esquerda = pagina.crop((0, 0, meio, altura))
            direita = pagina.crop((meio, 0, largura, altura))

            texto_esq = esquerda.extract_text()
            texto_dir = direita.extract_text()

            print(f"Processando página {i+1}...")

            # Se tem texto nas duas colunas → trata como 2 colunas
            if texto_esq and texto_dir:

                texto_final += "\n=== PAGINA {} (COLUNA ESQUERDA) ===\n".format(i+1)
                texto_final += texto_esq + "\n"

                texto_final += "\n=== PAGINA {} (COLUNA DIREITA) ===\n".format(i+1)
                texto_final += texto_dir + "\n"

            else:
                texto = pagina.extract_text()

                texto_final += "\n=== PAGINA {} ===\n".format(i+1)

                if texto:
                    texto_final += texto + "\n"

    return texto_final


def limpar_texto(texto):

    linhas = texto.split("\n")
    resultado = []

    for linha in linhas:

        linha = linha.strip()

        if not linha:
            continue

        upper = linha.upper()

        # remove cabeçalhos repetidos
        if "CURITIBA," in upper:
            continue

        if "RUA MARECHAL HERMES" in upper:
            continue

        if "SECRETARIA DE PUBLICAÇÕES OFICIAIS" in upper:
            continue

        resultado.append(linha)

    return "\n".join(resultado)


def salvar_txt(texto, path):

    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write(texto)

    print(f"\nArquivo salvo em: {path}")


def main():

    print("Convertendo PDF para texto...")

    texto = extrair_texto_corrigido(INPUT_PDF)

    #print("Limpando texto...")

    texto = limpar_texto(texto)

    salvar_txt(texto, OUTPUT_TXT)

    print("\nConcluído!")


if __name__ == "__main__":
    main()