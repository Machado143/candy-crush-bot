"""
Modelo de dados do tabuleiro do Candy Crush.

Cada peça guarda duas noções de posição, que nunca devem ser confundidas:
- posição de GRID (linha, coluna): índices lógicos no array 2D.
- posição de PIXEL (x, y): coordenada na tela, usada só quando formos
  clicar de verdade (Fase 5). Na simulação (Fase 2) fica em None.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Iterable


class TipoPeca(Enum):
    """Cores básicas do jogo + estados especiais."""
    VERMELHO = "vermelho"
    AMARELO = "amarelo"
    VERDE = "verde"
    AZUL = "azul"
    ROXO = "roxo"
    LARANJA = "laranja"
    VAZIO = "vazio"  # célula sem peça (ex: buraco temporário durante queda)


class Especial(Enum):
    """Modificador especial de uma peça, se houver."""
    NENHUM = "nenhum"
    LISTRADO_H = "listrado_h"   # limpa a linha inteira
    LISTRADO_V = "listrado_v"   # limpa a coluna inteira
    EMBRULHADO = "embrulhado"   # explode 3x3, duas vezes
    BOMBA_DE_COR = "bomba_de_cor"  # limpa todas as peças de uma cor


@dataclass
class Peca:
    tipo: TipoPeca
    linha: int
    coluna: int
    especial: Especial = Especial.NENHUM
    x: Optional[float] = None  # coordenada de pixel na tela (Fase 3+)
    y: Optional[float] = None

    @property
    def grid_xy(self) -> tuple[int, int]:
        """Posição no modelo de dados (linha, coluna)."""
        return (self.linha, self.coluna)

    @property
    def tela_xy(self) -> Optional[tuple[float, float]]:
        """Posição em pixel na tela, ou None se ainda não calibrado."""
        if self.x is None or self.y is None:
            return None
        return (self.x, self.y)

    # Abreviação de 1 letra por tipo, só para exibição compacta do tabuleiro.
    _ABREVIACOES = {
        TipoPeca.VERMELHO: "R", TipoPeca.AMARELO: "A", TipoPeca.VERDE: "V",
        TipoPeca.AZUL: "Z", TipoPeca.ROXO: "X", TipoPeca.LARANJA: "L",
        TipoPeca.VAZIO: ".",
    }

    def __repr__(self) -> str:
        marca = f"[{self.especial.value}]" if self.especial != Especial.NENHUM else ""
        return f"{self._ABREVIACOES.get(self.tipo, '?')}{marca}"


class Tabuleiro:
    def __init__(self, num_linhas: int, num_colunas: int):
        self.num_linhas = num_linhas
        self.num_colunas = num_colunas
        self._grade: List[List[Peca]] = [
            [Peca(TipoPeca.VAZIO, l, c) for c in range(num_colunas)]
            for l in range(num_linhas)
        ]

    def definir(self, linha: int, coluna: int, peca: Peca) -> None:
        peca.linha, peca.coluna = linha, coluna
        self._grade[linha][coluna] = peca

    def obter(self, linha: int, coluna: int) -> Optional[Peca]:
        if 0 <= linha < self.num_linhas and 0 <= coluna < self.num_colunas:
            return self._grade[linha][coluna]
        return None

    def vizinhos(self, linha: int, coluna: int) -> List[Peca]:
        """Vizinhos ortogonais válidos (cima, baixo, esquerda, direita)."""
        candidatos = [
            (linha - 1, coluna), (linha + 1, coluna),
            (linha, coluna - 1), (linha, coluna + 1),
        ]
        return [p for (l, c) in candidatos if (p := self.obter(l, c)) is not None]

    def trocar(self, l1: int, c1: int, l2: int, c2: int) -> None:
        """Troca duas peças de posição no grid (mantém suas coords de tela)."""
        p1, p2 = self._grade[l1][c1], self._grade[l2][c2]
        p1.linha, p1.coluna, p2.linha, p2.coluna = l2, c2, l1, c1
        self._grade[l1][c1], self._grade[l2][c2] = p2, p1

    def copiar_estado(self) -> "Tabuleiro":
        """Cópia profunda o suficiente para simular uma jogada sem afetar o original."""
        novo = Tabuleiro(self.num_linhas, self.num_colunas)
        for l in range(self.num_linhas):
            for c in range(self.num_colunas):
                original = self._grade[l][c]
                copia = Peca(
                    tipo=original.tipo,
                    linha=l,
                    coluna=c,
                    especial=original.especial,
                    x=original.x,
                    y=original.y,
                )
                novo._grade[l][c] = copia
        return novo

    def remover(self, celulas: Iterable[tuple[int, int]]) -> None:
        for l, c in celulas:
            self._grade[l][c] = Peca(TipoPeca.VAZIO, l, c)

    def aplicar_gravidade(self) -> None:
        for c in range(self.num_colunas):
            pilha = [
                self._grade[l][c]
                for l in range(self.num_linhas)
                if self._grade[l][c].tipo != TipoPeca.VAZIO
            ]

            num_vazios = self.num_linhas - len(pilha)
            for l in range(num_vazios):
                self._grade[l][c] = Peca(TipoPeca.VAZIO, l, c)

            for i, peca in enumerate(pilha):
                l_destino = num_vazios + i
                peca.linha, peca.coluna = l_destino, c
                self._grade[l_destino][c] = peca

    def preencher_vazios(self, gerador_aleatorio=None) -> None:
        import random

        rnd = gerador_aleatorio or random
        cores = [t for t in TipoPeca if t != TipoPeca.VAZIO]

        for l in range(self.num_linhas):
            for c in range(self.num_colunas):
                if self._grade[l][c].tipo == TipoPeca.VAZIO:
                    self._grade[l][c] = Peca(rnd.choice(cores), l, c)

    def __repr__(self) -> str:
        linhas = []
        for l in range(self.num_linhas):
            linhas.append(" ".join(f"{self._grade[l][c]!r:>3}" for c in range(self.num_colunas)))
        return "\n".join(linhas)
