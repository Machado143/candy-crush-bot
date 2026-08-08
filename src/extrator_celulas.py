from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from detector_grade import DetectorGrade
from geometria_grade import GeometriaGrade


class ExtratorCelulas:
    """
    Extrai cada célula individual de um tabuleiro
    a partir da geometria detectada.
    """

    def extrair(
        self,
        imagem: np.ndarray,
        grade: GeometriaGrade,
    ) -> dict[tuple[int, int], np.ndarray]:

        if imagem is None:
            raise ValueError(
                "Imagem inválida."
            )

        celulas: dict[
            tuple[int, int],
            np.ndarray,
        ] = {}

        altura, largura = imagem.shape[:2]

        for linha in range(grade.linhas):

            for coluna in range(grade.colunas):

                x1, y1, x2, y2 = grade.limites(
                    linha,
                    coluna,
                )

                # Garante que os limites estejam
                # dentro da imagem.
                x1 = max(0, min(x1, largura))
                x2 = max(0, min(x2, largura))
                y1 = max(0, min(y1, altura))
                y2 = max(0, min(y2, altura))

                if x2 <= x1 or y2 <= y1:
                    raise RuntimeError(
                        f"Célula inválida: "
                        f"({linha}, {coluna})"
                    )

                celula = imagem[
                    y1:y2,
                    x1:x2,
                ].copy()

                celulas[
                    (linha, coluna)
                ] = celula

        return celulas

    def salvar(
        self,
        celulas: dict[
            tuple[int, int],
            np.ndarray,
        ],
        diretorio: Path,
    ) -> None:

        diretorio.mkdir(
            parents=True,
            exist_ok=True,
        )

        for (
            linha,
            coluna,
        ), imagem in celulas.items():

            caminho = diretorio / (
                f"{linha:02d}_{coluna:02d}.png"
            )

            sucesso = cv2.imwrite(
                str(caminho),
                imagem,
            )

            if not sucesso:
                raise RuntimeError(
                    f"Não foi possível salvar: "
                    f"{caminho}"
                )


def desenhar_indices(
    imagem: np.ndarray,
    grade: GeometriaGrade,
) -> np.ndarray:

    debug = imagem.copy()

    for linha in range(grade.linhas):

        for coluna in range(grade.colunas):

            x1, y1, x2, y2 = grade.limites(
                linha,
                coluna,
            )

            centro_x, centro_y = grade.centro(
                linha,
                coluna,
            )

            cv2.rectangle(
                debug,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2,
            )

            texto = f"{linha},{coluna}"

            cv2.putText(
                debug,
                texto,
                (
                    centro_x - 12,
                    centro_y,
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

    return debug


def main() -> None:

    caminho_imagem = Path(
        "imagens_teste/tabuleiro.png"
    )

    imagem = cv2.imread(
        str(caminho_imagem)
    )

    if imagem is None:
        raise FileNotFoundError(
            f"Imagem não encontrada: "
            f"{caminho_imagem}"
        )

    print(
        f"Imagem: "
        f"{imagem.shape[1]}x"
        f"{imagem.shape[0]}"
    )

    # -------------------------------------------------
    # 1. Detecta a grade
    # -------------------------------------------------

    detector = DetectorGrade()

    grade = detector.detectar(
        imagem,
        linhas=7,
        colunas=7,
    )

    print()
    print("=== GRADE ===")
    print(
        "X:",
        grade.limites_x,
    )
    print(
        "Y:",
        grade.limites_y,
    )

    # -------------------------------------------------
    # 2. Extrai as células
    # -------------------------------------------------

    extrator = ExtratorCelulas()

    celulas = extrator.extrair(
        imagem,
        grade,
    )

    print()
    print(
        f"Células extraídas: "
        f"{len(celulas)}"
    )

    # -------------------------------------------------
    # 3. Salva as células
    # -------------------------------------------------

    diretorio = Path(
        "imagens_teste/celulas"
    )

    extrator.salvar(
        celulas,
        diretorio,
    )

    print(
        f"Células salvas em: "
        f"{diretorio}"
    )

    # -------------------------------------------------
    # 4. Debug
    # -------------------------------------------------

    debug = desenhar_indices(
        imagem,
        grade,
    )

    caminho_debug = Path(
        "imagens_teste/"
        "debug_celulas.png"
    )

    if not cv2.imwrite(
        str(caminho_debug),
        debug,
    ):
        raise RuntimeError(
            "Não foi possível salvar "
            "o debug."
        )

    print(
        f"Debug salvo em: "
        f"{caminho_debug}"
    )


if __name__ == "__main__":
    main()