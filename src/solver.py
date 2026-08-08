"""
Solver guloso (sem lookahead) para o Candy Crush.

Estratégia: para cada jogada adjacente válida, simula a troca num tabuleiro
copiado, detecta os matches resultantes e calcula uma pontuação. No final,
escolhe a jogada de maior pontuação.

Heurística de pontuação (baseada nas regras conhecidas do jogo):
- match de 3:                    pontuação base
- match de 4 em linha/coluna:    cria peça listrada -> bônus alto
- match em L ou T:               cria peça embrulhada -> bônus alto
- match de 5 em linha:           cria bomba de cor -> bônus máximo
- combinar dois especiais:       bônus extra (não implementado na v1;
                                  fica para a Fase 7, junto do lookahead)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Set, Tuple

from modelo import Tabuleiro, TipoPeca, Especial

# Pontuações base por tipo de resultado de match
PONTOS_MATCH_3 = 10
PONTOS_MATCH_4 = 40      # cria listrado
PONTOS_MATCH_L_T = 50    # cria embrulhado
PONTOS_MATCH_5 = 100     # cria bomba de cor


@dataclass
class Jogada:
    l1: int
    c1: int
    l2: int
    c2: int
    pontuacao: float

    def __repr__(self) -> str:
        return f"Jogada(({self.l1},{self.c1}) <-> ({self.l2},{self.c2})) = {self.pontuacao} pts"


def _encontrar_linhas_de_match(tabuleiro: Tabuleiro) -> List[Set[Tuple[int, int]]]:
    """
    Encontra todos os grupos de 3+ peças do mesmo tipo, alinhadas horizontal
    ou verticalmente. Retorna uma lista de conjuntos de coordenadas (l, c),
    um conjunto por sequência contígua encontrada.
    """
    grupos: List[Set[Tuple[int, int]]] = []

    # Varredura horizontal
    for l in range(tabuleiro.num_linhas):
        c = 0
        while c < tabuleiro.num_colunas:
            peca = tabuleiro.obter(l, c)
            if peca is None or peca.tipo == TipoPeca.VAZIO:
                c += 1
                continue
            fim = c
            while fim + 1 < tabuleiro.num_colunas:
                seguinte = tabuleiro.obter(l, fim + 1)
                if seguinte is not None and seguinte.tipo == peca.tipo:
                    fim += 1
                else:
                    break
            if fim - c + 1 >= 3:
                grupos.append({(l, x) for x in range(c, fim + 1)})
            c = fim + 1

    # Varredura vertical
    for c in range(tabuleiro.num_colunas):
        l = 0
        while l < tabuleiro.num_linhas:
            peca = tabuleiro.obter(l, c)
            if peca is None or peca.tipo == TipoPeca.VAZIO:
                l += 1
                continue
            fim = l
            while fim + 1 < tabuleiro.num_linhas:
                seguinte = tabuleiro.obter(fim + 1, c)
                if seguinte is not None and seguinte.tipo == peca.tipo:
                    fim += 1
                else:
                    break
            if fim - l + 1 >= 3:
                grupos.append({(x, c) for x in range(l, fim + 1)})
            l = fim + 1

    return grupos


def _pontuar_grupos(grupos: List[Set[Tuple[int, int]]]) -> float:
    """
    Calcula a pontuação total de uma jogada a partir dos grupos de match
    encontrados. Detecta L/T quando um grupo horizontal e um vertical se
    cruzam na mesma peça.
    """
    if not grupos:
        return 0.0

    total = 0.0

    # Detecta cruzamentos (L/T): duas células que aparecem em grupos
    # diferentes indicam um cruzamento horizontal+vertical na mesma jogada.
    todas_celulas: List[Tuple[int, int]] = []
    for g in grupos:
        todas_celulas.extend(g)
    celulas_repetidas = {cel for cel in todas_celulas if todas_celulas.count(cel) > 1}

    if celulas_repetidas:
        total += PONTOS_MATCH_L_T
        # desconta os grupos que geraram o cruzamento para não contar 2x
        grupos_usados_no_cruzamento = [g for g in grupos if g & celulas_repetidas]
        for g in grupos_usados_no_cruzamento:
            grupos = [x for x in grupos if x is not g]

    for grupo in grupos:
        tamanho = len(grupo)
        if tamanho >= 5:
            total += PONTOS_MATCH_5
        elif tamanho == 4:
            total += PONTOS_MATCH_4
        else:  # tamanho == 3
            total += PONTOS_MATCH_3

    return total


def avaliar_jogada(
    tabuleiro: Tabuleiro,
    l1: int,
    c1: int,
    l2: int,
    c2: int,
    max_cascatas: int = 20,
    gerador_aleatorio=None,
) -> float:
    copia = tabuleiro.copiar_estado()
    copia.trocar(l1, c1, l2, c2)

    total = 0.0
    for _ in range(max_cascatas):
        grupos = _encontrar_linhas_de_match(copia)
        if not grupos:
            break

        total += _pontuar_grupos(grupos)

        celulas_para_remover = set()
        for grupo in grupos:
            celulas_para_remover |= grupo

        copia.remover(celulas_para_remover)
        copia.aplicar_gravidade()
        copia.preencher_vazios(gerador_aleatorio)

    return total


def gerar_jogadas_possiveis(tabuleiro: Tabuleiro) -> List[Jogada]:
    """
    Gera todas as trocas adjacentes possíveis no tabuleiro e retorna apenas
    as que pontuam (match válido), já com a pontuação calculada.
    """
    jogadas: List[Jogada] = []
    vistas: Set[Tuple[int, int, int, int]] = set()

    for l in range(tabuleiro.num_linhas):
        for c in range(tabuleiro.num_colunas):
            peca_atual = tabuleiro.obter(l, c)
            if peca_atual is None or peca_atual.tipo == TipoPeca.MAQUINA:
                continue
            for (l2, c2) in [(l, c + 1), (l + 1, c)]:  # direita e abaixo evita duplicar pares
                vizinho = tabuleiro.obter(l2, c2)
                if vizinho is None or vizinho.tipo == TipoPeca.MAQUINA:
                    continue
                chave = (l, c, l2, c2)
                if chave in vistas:
                    continue
                vistas.add(chave)

                pontuacao = avaliar_jogada(tabuleiro, l, c, l2, c2)
                if pontuacao > 0:
                    jogadas.append(Jogada(l, c, l2, c2, pontuacao))

    return jogadas


def melhor_jogada(tabuleiro: Tabuleiro) -> Jogada | None:
    """Retorna a jogada de maior pontuação disponível, ou None se não houver nenhuma."""
    jogadas = gerar_jogadas_possiveis(tabuleiro)
    if not jogadas:
        return None
    return max(jogadas, key=lambda j: j.pontuacao)
