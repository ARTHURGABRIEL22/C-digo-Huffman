import os
from collections import defaultdict

class NodoHuffman:
    def __init__(self, caractere, frequencia):
        self.caractere = caractere
        self.frequencia = frequencia
        self.esquerda = None
        self.direita = None

class ArvoreHuffman:
    def __init__(self, mapa_frequencia_caracteres):
        self.mapa_frequencia_caracteres = mapa_frequencia_caracteres
        self.raiz = self.construir_arvore()

    def construir_arvore(self):
        nodos = [NodoHuffman(caractere, frequencia) for caractere, frequencia in self.mapa_frequencia_caracteres.items()]

        while len(nodos) > 1:
            nodos.sort(key=lambda nodo: nodo.frequencia)

            esquerda = nodos.pop(0)
            direita = nodos.pop(0)

            nodo_fusao = NodoHuffman(None, esquerda.frequencia + direita.frequencia)
            nodo_fusao.esquerda = esquerda
            nodo_fusao.direita = direita

            nodos.append(nodo_fusao)

        return nodos[0]

    def construir_codigos(self, nodo=None, codigo="", codigos=None):
        if codigos is None:
            codigos = {}

        if nodo is None:
            nodo = self.raiz

        if nodo.caractere:
            codigos[nodo.caractere] = codigo
        else:
            self.construir_codigos(nodo.esquerda, codigo + "0", codigos)
            self.construir_codigos(nodo.direita, codigo + "1", codigos)

        return codigos


class Compactador:
    def __init__(self, caminho_arquivo_entrada):
        self.caminho_arquivo_entrada = caminho_arquivo_entrada
        self.mapa_frequencia_caracteres = self.contar_caracteres()
        self.arvore_huffman = ArvoreHuffman(self.mapa_frequencia_caracteres)
        self.codigos = self.arvore_huffman.construir_codigos()

    def contar_caracteres(self):
        mapa_frequencia_caracteres = {}

        with open(self.caminho_arquivo_entrada, "r", encoding="ISO-8859-1") as arquivo:
            conteudo = arquivo.read()
            for caractere in conteudo:
                mapa_frequencia_caracteres[caractere] = mapa_frequencia_caracteres.get(caractere, 0) + 1

        return mapa_frequencia_caracteres

    def compactar(self, caminho_arquivo_saida):
        with open(caminho_arquivo_saida, "wb") as arquivo_saida:
            num_caracteres = len(self.codigos)
            arquivo_saida.write(num_caracteres.to_bytes(1, byteorder="big"))

            for caractere, codigo in self.codigos.items():
                ascii_caractere = ord(caractere)
                tamanho_codigo = len(codigo)
                arquivo_saida.write(ascii_caractere.to_bytes(1, byteorder="big"))
                arquivo_saida.write(tamanho_codigo.to_bytes(1, byteorder="big"))
                codigo_inteiro = int(codigo, 2)
                tamanho_bytes_codigo = (tamanho_codigo + 7) // 8
                arquivo_saida.write(codigo_inteiro.to_bytes(tamanho_bytes_codigo, byteorder="big"))

            conteudo_codificado = self.codificar_conteudo()
            bits_padding = 8 - len(conteudo_codificado) % 8
            conteudo_codificado += "0" * bits_padding
            conteudo_codificado_bytes = bytes([int(conteudo_codificado[i:i + 8], 2) for i in range(0, len(conteudo_codificado), 8)])
            arquivo_saida.write(conteudo_codificado_bytes)

    def codificar_conteudo(self):
        conteudo = open(self.caminho_arquivo_entrada, "r", encoding="ISO-8859-1").read()
        conteudo_codificado = "".join(self.codigos[caractere] for caractere in conteudo)
        return conteudo_codificado


class Descompactador:
    def __init__(self, caminho_arquivo_entrada):
        self.caminho_arquivo_entrada = caminho_arquivo_entrada
        self.codigos = {}
        self.conteudo_codificado = b""
        self.num_caracteres = 0

    def ler_codigos(self):
        with open(self.caminho_arquivo_entrada, "rb") as arquivo_entrada:
            num_caracteres = int.from_bytes(arquivo_entrada.read(1), byteorder="big")

            for _ in range(num_caracteres):
                ascii_caractere = int.from_bytes(arquivo_entrada.read(1), byteorder="big")
                tamanho_codigo = int.from_bytes(arquivo_entrada.read(1), byteorder="big")
                tamanho_bytes_codigo = (tamanho_codigo + 7) // 8
                codigo_inteiro = int.from_bytes(arquivo_entrada.read(tamanho_bytes_codigo), byteorder="big")
                codigo_binario = bin(codigo_inteiro)[2:].rjust(tamanho_codigo, "0")

                caractere = chr(ascii_caractere)
                self.codigos[codigo_binario] = caractere

            self.conteudo_codificado = arquivo_entrada.read()

    def descompactar(self, caminho_arquivo_saida):
        self.ler_codigos()
        codigo_atual = ""
        conteudo_decodificado = []

        for byte in self.conteudo_codificado:
            byte_atual = format(byte, '08b')

            for bit in byte_atual:
                codigo_atual += bit

                if codigo_atual in self.codigos:
                    conteudo_decodificado.append(self.codigos[codigo_atual])
                    codigo_atual = ""

        conteudo_decodificado_str = "".join(conteudo_decodificado)
        conteudo_decodificado_str = conteudo_decodificado_str[:-2]

        with open(caminho_arquivo_saida, "wb") as arquivo_saida:
            arquivo_saida.write(conteudo_decodificado_str.encode("ISO-8859-1"))

def contar_caracteres_no_arquivo(caminho_arquivo):
    contagem_caracteres = defaultdict(int)

    with open(caminho_arquivo, 'r', encoding='ISO-8859-1') as arquivo:
        for linha in arquivo:
            for caractere in linha:
                contagem_caracteres[caractere] += 1

    return contagem_caracteres

def mostrar_representacao_binaria(contagem_caracteres):
    for caractere, contagem in contagem_caracteres.items():
        ascii_caractere = ord(caractere)
        representacao_binaria = bin(ascii_caractere)[2:].zfill(8)
        print(f"'{caractere}': {contagem} ({representacao_binaria})")

# Uso de exemplo:

caminho_arquivo_entrada = "poesias-margareth.txt"
caminho_arquivo_saida = "poesias-margareth.uzip"

contagem_caracteres = contar_caracteres_no_arquivo(caminho_arquivo_entrada)

compactador = Compactador(caminho_arquivo_entrada)
compactador.compactar(caminho_arquivo_saida)

tamanho_original = os.path.getsize(caminho_arquivo_entrada)
tamanho_compactado = os.path.getsize(caminho_arquivo_saida)
print("\nTamanho original do arquivo:", tamanho_original, "bytes")
print("Tamanho do arquivo compactado:", tamanho_compactado, "bytes")

caminho_arquivo_entrada = "poesias-margareth.uzip"
caminho_arquivo_saida_descompactado = "poesias-margareth-descompactado.txt"

descompactador = Descompactador(caminho_arquivo_entrada)
descompactador.descompactar(caminho_arquivo_saida_descompactado)

tamanho_descompactado = os.path.getsize(caminho_arquivo_saida_descompactado)
print("Tamanho do arquivo descompactado:", tamanho_descompactado, "bytes")

print("\nRepresentação binária dos caracteres:")
mostrar_representacao_binaria(contagem_caracteres)
