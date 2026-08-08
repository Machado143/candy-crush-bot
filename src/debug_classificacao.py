from __future__ import annotations

from pathlib import Path

import cv2

from classificador_cor import ClassificadorCor
from visao import carregar_celulas


def main() -> None:
    caminho = Path(
        "imagens_teste/tabuleiro.png"
    )

    imagem = cv2.imread(str(caminho))

    if imagem is None:
        raise FileNotFoundError(
            f"Imagem não encontrada: {caminho}"
        )

    resultados = carregar_celulas()

    classificador = ClassificadorCor()

    debug = imagem.copy()

    print("=== CLASSIFICAÇÃO DETALHADA ===")

    for celula in resultados:

        resultado = classificador.classificar(
            matiz=celula.matiz_dominante,
            saturacao=celula.saturacao,
            brilho=celula.brilho,
        )

        x1 = 169 + round(
            celula.coluna * (
                (621 - 169) / 7
            )
        )

        y1 = 134 + round(
            celula.linha * (
                (618 - 134) / 7
            )
        )

        x2 = 169 + round(
            (celula.coluna + 1) * (
                (621 - 169) / 7
            )
        )

        y2 = 134 + round(
            (celula.linha + 1) * (
                (618 - 134) / 7
            )
        )

        centro_x = (x1 + x2) // 2
        centro_y = (y1 + y2) // 2

        cv2.rectangle(
            debug,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2,
        )

        texto = resultado.categoria.replace(
            "grupo_",
            "G",
        )

        cv2.putText(
            debug,
            texto,
            (
                centro_x - 10,
                centro_y,
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

        print(
            f"({celula.linha},{celula.coluna}) "
            f"{resultado.categoria} "
            f"H={celula.matiz_dominante:.0f} "
            f"S={celula.saturacao:.1f} "
            f"V={celula.brilho:.1f} "
            f"dist={resultado.distancia:.2f} "
            f"conf={resultado.confianca:.2f}%"
        )

    saida = Path(
        "imagens_teste/"
        "debug_classificacao.png"
    )

    if not cv2.imwrite(
        str(saida),
        debug,
    ):
        raise RuntimeError(
            f"Não foi possível salvar: {saida}"
        )

    print()
    print(
        f"Debug salvo em: {saida}"
    )


if __name__ == "__main__":
    main()