from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(frozen=True)
class Periodicidade:
    tamanho: float
    erro: float


class DetectorPeriodicidade:

    def detectar(
        self,
        imagem: np.ndarray,
        minimo: int = 50,
        maximo: int = 130,
    ) -> tuple[Periodicidade, Periodicidade]:

        if imagem is None:
            raise ValueError(
                "Imagem inválida."
            )

        cinza = cv2.cvtColor(
            imagem,
            cv2.COLOR_BGR2GRAY,
        )

        # Remove pequenas variações.
        cinza = cv2.GaussianBlur(
            cinza,
            (9, 9),
            0,
        )

        # -------------------------------------------------
        # Procuramos periodicidade horizontal e vertical.
        # -------------------------------------------------

        erro_x = self._avaliar_periodos(
            cinza,
            eixo=1,
            minimo=minimo,
            maximo=maximo,
        )

        erro_y = self._avaliar_periodos(
            cinza,
            eixo=0,
            minimo=minimo,
            maximo=maximo,
        )

        melhor_x = min(
            erro_x,
            key=lambda item: item.erro,
        )

        melhor_y = min(
            erro_y,
            key=lambda item: item.erro,
        )

        return melhor_x, melhor_y

    def _avaliar_periodos(
        self,
        imagem: np.ndarray,
        eixo: int,
        minimo: int,
        maximo: int,
    ) -> list[Periodicidade]:

        resultados = []

        for periodo in range(
            minimo,
            maximo + 1,
        ):

            if eixo == 1:
                deslocada = imagem[
                    :,
                    periodo:,
                ]

                original = imagem[
                    :,
                    :-periodo,
                ]

            else:
                deslocada = imagem[
                    periodo:,
                    :,
                ]

                original = imagem[
                    :-periodo,
                    :,
                ]

            if (
                deslocada.size == 0
                or original.size == 0
            ):
                continue

            # Diferença absoluta entre a imagem e
            # ela mesma deslocada pelo período.
            diferenca = cv2.absdiff(
                original,
                deslocada,
            )

            erro = float(
                np.mean(diferenca)
            )

            resultados.append(
                Periodicidade(
                    tamanho=float(periodo),
                    erro=erro,
                )
            )

        return resultados


def main() -> None:

    caminho = (
        "imagens_teste/"
        "tabuleiro.png"
    )

    imagem = cv2.imread(
        caminho
    )

    if imagem is None:
        raise FileNotFoundError(
            caminho
        )

    detector = DetectorPeriodicidade()

    x, y = detector.detectar(
        imagem
    )

    print()
    print("=== PERIODICIDADE ===")

    print(
        f"X: {x.tamanho:.2f}px "
        f"(erro={x.erro:.2f})"
    )

    print(
        f"Y: {y.tamanho:.2f}px "
        f"(erro={y.erro:.2f})"
    )


if __name__ == "__main__":
    main()