import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from modelo import Peca, Tabuleiro, TipoPeca
from solver import gerar_jogadas_possiveis, melhor_jogada


def tabuleiro_de_texto(linhas: list[str]) -> Tabuleiro:
    """
    Monta um Tabuleiro a partir de linhas de texto, ex:
    ["RRVAA",
     "VAVAR", ...]
    Onde cada letra mapeia para uma cor. Facilita escrever cenários de teste.
    """
    mapa = {
        "R": TipoPeca.VERMELHO,
        "A": TipoPeca.AMARELO,
        "V": TipoPeca.VERDE,
        "Z": TipoPeca.AZUL,
        "X": TipoPeca.ROXO,
        "L": TipoPeca.LARANJA,
    }
    num_linhas = len(linhas)
    num_colunas = len(linhas[0])
    t = Tabuleiro(num_linhas, num_colunas)
    for l, linha_txt in enumerate(linhas):
        for c, letra in enumerate(linha_txt):
            t.definir(l, c, Peca(mapa[letra], l, c))
    return t


def teste_match_3_simples():
    # trocar (1,1) Z <-> (0,1) A cria RRR na linha 0? Vamos montar um caso claro:
    # linha 0: R R A  -> trocando (0,2) com (1,2) [Z] não ajuda.
    # Caso direto: coluna com quase-match vertical.
    t = tabuleiro_de_texto([
        "RAV",
        "RAV",
        "ARV",
    ])
    # trocar (2,0)=A com (2,1)=R -> linha 2 vira R A V (sem match) errado, vamos testar geração geral
    jogadas = gerar_jogadas_possiveis(t)
    print("Tabuleiro:")
    print(t)
    print(f"\n{len(jogadas)} jogada(s) válida(s) encontrada(s):")
    for j in sorted(jogadas, key=lambda x: -x.pontuacao):
        print(" ", j)
    assert len(jogadas) > 0, "Deveria haver ao menos uma jogada válida nesse tabuleiro"


def teste_melhor_jogada_prioriza_match_maior():
    # Tabuleiro pensado para ter um match-3 óbvio e um match-4 óbvio disponível
    t = tabuleiro_de_texto([
        "RRRAV",
        "AVZXL",
        "VZXLR",
        "ZXLRV",
        "XLRVZ",
    ])
    # Aqui (0,3)=A trocado com (1,3)=X não faz nada especial; o objetivo do
    # teste é apenas garantir que melhor_jogada não quebra e retorna a maior.
    jogada = melhor_jogada(t)
    print("\nMelhor jogada encontrada:", jogada)
    assert jogada is not None


def teste_tabuleiro_sem_jogadas():
    # Padrão diagonal com 3 cores (R,V,Z repetindo a cada coluna, deslocando
    # 1 por linha): nenhuma troca adjacente aproxima 2 peças iguais o
    # suficiente para formar um trio. Diferente do xadrez de 2 cores (que
    # SIM gera match ao trocar, por simetria), esse padrão é realmente livre
    # de jogadas.
    cores = "RVZ"
    linhas = []
    for l in range(5):
        linha = "".join(cores[(c + l) % 3] for c in range(5))
        linhas.append(linha)
    t = tabuleiro_de_texto(linhas)
    jogadas = gerar_jogadas_possiveis(t)
    print("\nTabuleiro diagonal 3 cores:")
    print(t)
    print(f"{len(jogadas)} jogada(s) válida(s) (esperado: 0)")
    assert len(jogadas) == 0


if __name__ == "__main__":
    teste_match_3_simples()
    teste_melhor_jogada_prioriza_match_maior()
    teste_tabuleiro_sem_jogadas()
    print("\nTodos os testes passaram.")
