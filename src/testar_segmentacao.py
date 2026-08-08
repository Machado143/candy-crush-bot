from __future__ import annotations

from pathlib import Path

import cv2

from segmentador_objeto import (
    segmentar_objeto,
)


def main() -> None:

    diretorio = Path(
        "imagens_teste/celulas"
    )

    saida = Path(
        "imagens_teste/segmentadas"
    )

    saida.mkdir(
        parents=True,
        exist_ok=True,
    )

    arquivos = sorted(
        diretorio.glob("*.png")
    )

    for arquivo in arquivos:

        imagem = cv2.imread(
            str(arquivo)
        )

        if imagem is None:
            continue

        resultado = segmentar_objeto(
            imagem
        )

        visualizacao = cv2.cvtColor(
            resultado.mascara,
            cv2.COLOR_GRAY2BGR,
        )

        nome = arquivo.stem

        caminho_saida = (
            saida / f"{nome}_mask.png"
        )

        cv2.imwrite(
            str(caminho_saida),
            visualizacao,
        )

        print(
            f"{nome}: "
            f"area={resultado.area_objeto} "
            f"objeto="
            f"{resultado.percentual_objeto:.1f}% "
            f"centro=("
            f"{resultado.centro_x:.1f}, "
            f"{resultado.centro_y:.1f})"
        )


if __name__ == "__main__":
    main()