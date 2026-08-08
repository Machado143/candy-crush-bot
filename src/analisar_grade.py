from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


def main() -> None:
    caminho = Path(
        "imagens_teste/tabuleiro.png"
    )

    imagem = cv2.imread(
        str(caminho)
    )

    if imagem is None:
        raise FileNotFoundError(
            f"Imagem não encontrada: {caminho}"
        )

    altura, largura = imagem.shape[:2]

    print(
        f"Imagem: {largura}x{altura}"
    )

    # -------------------------------------------------
    # Escala de cinza
    # -------------------------------------------------

    cinza = cv2.cvtColor(
        imagem,
        cv2.COLOR_BGR2GRAY,
    )

    # -------------------------------------------------
    # Gradiente horizontal
    #
    # Destaca mudanças na vertical.
    # Útil para procurar limites entre colunas.
    # -------------------------------------------------

    grad_x = cv2.Sobel(
        cinza,
        cv2.CV_64F,
        1,
        0,
        ksize=3,
    )

    grad_x = np.abs(grad_x)

    perfil_x = np.mean(
        grad_x,
        axis=0,
    )

    # -------------------------------------------------
    # Gradiente vertical
    #
    # Destaca mudanças na horizontal.
    # Útil para procurar limites entre linhas.
    # -------------------------------------------------

    grad_y = cv2.Sobel(
        cinza,
        cv2.CV_64F,
        0,
        1,
        ksize=3,
    )

    grad_y = np.abs(grad_y)

    perfil_y = np.mean(
        grad_y,
        axis=1,
    )

    # -------------------------------------------------
    # Normalização
    # -------------------------------------------------

    perfil_x = (
        perfil_x
        / max(
            perfil_x.max(),
            1,
        )
        * 255
    )

    perfil_y = (
        perfil_y
        / max(
            perfil_y.max(),
            1,
        )
        * 255
    )

    perfil_x = perfil_x.astype(
        np.uint8
    )

    perfil_y = perfil_y.astype(
        np.uint8
    )

    # -------------------------------------------------
    # Imagem de debug
    # -------------------------------------------------

    debug = imagem.copy()

    # Perfil X no topo.
    altura_grafico = 120

    grafico_x = np.zeros(
        (
            altura_grafico,
            largura,
            3,
        ),
        dtype=np.uint8,
    )

    for x in range(largura):
        valor = int(
            perfil_x[x]
        )

        y = (
            altura_grafico
            - 1
            - int(
                valor
                * (altura_grafico - 1)
                / 255
            )
        )

        cv2.line(
            grafico_x,
            (x, altura_grafico - 1),
            (x, y),
            (255, 255, 255),
            1,
        )

    # Perfil Y na lateral.
    largura_grafico = 120

    grafico_y = np.zeros(
        (
            altura,
            largura_grafico,
            3,
        ),
        dtype=np.uint8,
    )

    for y in range(altura):
        valor = int(
            perfil_y[y]
        )

        x = int(
            valor
            * (largura_grafico - 1)
            / 255
        )

        cv2.line(
            grafico_y,
            (0, y),
            (x, y),
            (255, 255, 255),
            1,
        )

    # -------------------------------------------------
    # Salva os perfis
    # -------------------------------------------------

    cv2.imwrite(
        "imagens_teste/"
        "perfil_x.png",
        grafico_x,
    )

    cv2.imwrite(
        "imagens_teste/"
        "perfil_y.png",
        grafico_y,
    )

    # -------------------------------------------------
    # Imprime os maiores picos
    # -------------------------------------------------

    indices_x = np.argsort(
        perfil_x
    )[::-1]

    indices_y = np.argsort(
        perfil_y
    )[::-1]

    print()
    print(
        "Maiores regiões de mudança X:"
    )

    vistos = []

    for indice in indices_x:

        indice = int(indice)

        if any(
            abs(indice - x) < 10
            for x in vistos
        ):
            continue

        vistos.append(indice)

        print(
            f"X={indice}: "
            f"{perfil_x[indice]}"
        )

        if len(vistos) >= 20:
            break

    print()
    print(
        "Maiores regiões de mudança Y:"
    )

    vistos = []

    for indice in indices_y:

        indice = int(indice)

        if any(
            abs(indice - y) < 10
            for y in vistos
        ):
            continue

        vistos.append(indice)

        print(
            f"Y={indice}: "
            f"{perfil_y[indice]}"
        )

        if len(vistos) >= 20:
            break

    print()
    print(
        "Arquivos gerados:"
    )
    print(
        "imagens_teste/perfil_x.png"
    )
    print(
        "imagens_teste/perfil_y.png"
    )


if __name__ == "__main__":
    main()