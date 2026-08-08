from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GeometriaGrade:
    limites_x: tuple[int, ...]
    limites_y: tuple[int, ...]

    @property
    def colunas(self) -> int:
        return len(self.limites_x) - 1

    @property
    def linhas(self) -> int:
        return len(self.limites_y) - 1

    def limites(
        self,
        linha: int,
        coluna: int,
    ) -> tuple[int, int, int, int]:

        if not 0 <= linha < self.linhas:
            raise IndexError(
                f"Linha inválida: {linha}"
            )

        if not 0 <= coluna < self.colunas:
            raise IndexError(
                f"Coluna inválida: {coluna}"
            )

        x1 = self.limites_x[coluna]
        x2 = self.limites_x[coluna + 1]

        y1 = self.limites_y[linha]
        y2 = self.limites_y[linha + 1]

        return x1, y1, x2, y2

    def centro(
        self,
        linha: int,
        coluna: int,
    ) -> tuple[int, int]:

        x1, y1, x2, y2 = self.limites(
            linha,
            coluna,
        )

        return (
            round((x1 + x2) / 2),
            round((y1 + y2) / 2),
        )