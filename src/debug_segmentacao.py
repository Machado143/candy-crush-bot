from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from extrator_celulas import ExtratorCelulas
from detector_grade import DetectorGrade
from segmentador_doce import SegmentadorDoce


CAMINHO_IMAGEM = Path("imagens_teste/imagem.png")
DIRETORIO_CELULAS = Path("imagens_teste/celulas")
DIRETORIO_DEBUG = Path("imagens_teste/debug_segmentacao")


def carregar_celulas() -> list[tuple[int, int, np.ndarray]]:
    arquivos = sorted(DIRETORIO_CELULAS.glob("*.png"))

    if not arquivos:
        raise RuntimeError(
            f"Nenhuma célula encontrada em: {DIRETORIO_CELULAS}"
        )

    resultado = []

    for arquivo in arquivos:
        try:
            nome = arquivo.stem
            linha, coluna = map(int, nome.split("_"))

            imagem = cv2.imread(str(arquivo))

            if imagem is None:
                print(f"[AVISO] Não foi possível ler: {arquivo}")
                continue

            resultado.append((linha, coluna, imagem))

        except ValueError:
            print(f"[AVISO] Nome ignorado: {arquivo.name}")

    return resultado


def salvar_debug(
    linha: int,
    coluna: int,
    imagem: np.ndarray,
    mascara: np.ndarray,
) -> None:
    DIRETORIO_DEBUG.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Máscara em escala de cinza.
    caminho_mascara = (
        DIRETORIO_DEBUG / f"{linha:02d}_{coluna:02d}_mascara.png"
    )

    cv2.imwrite(
        str(caminho_mascara),
        mascara,
    )

    # Visualização: regiões detectadas ficam coloridas.
    visualizacao = imagem.copy()

    visualizacao[mascara == 0] = (
        visualizacao[mascara == 0] * 0.25
    ).astype(np.uint8)

    caminho_visualizacao = (
        DIRETORIO_DEBUG / f"{linha:02d}_{coluna:02d}_debug.png"
    )

    cv2.imwrite(
        str(caminho_visualizacao),
        visualizacao,
    )


def gerar_mosaico(
    resultados: list[tuple[int, int, float, np.ndarray]],
) -> np.ndarray:
    tamanho = 7

    celulas: dict[tuple[int, int], np.ndarray] = {
        (linha, coluna): imagem
        for linha, coluna, _, imagem in resultados
    }

    imagens = []

    for linha in range(tamanho):
        linha_imagens = []

        for coluna in range(tamanho):
            imagem = celulas.get((linha, coluna))

            if imagem is None:
                imagem = np.zeros((100, 100, 3), dtype=np.uint8)

            imagem = cv2.resize(
                imagem,
                (100, 100),
                interpolation=cv2.INTER_NEAREST,
            )

            linha_imagens.append(imagem)

        imagens.append(np.hstack(linha_imagens))

    return np.vstack(imagens)


def main() -> None:
    print("=== DEBUG SEGMENTAÇÃO ===")

    celulas = carregar_celulas()

    print(f"Células encontradas: {len(celulas)}")

    segmentador = SegmentadorDoce()

    resultados = []

    for linha, coluna, imagem in celulas:
        resultado = segmentador.segmentar(imagem)

        salvar_debug(
            linha,
            coluna,
            imagem,
            resultado.mascara,
        )

        resultados.append(
            (
                linha,
                coluna,
                resultado.percentual_doce,
                resultado.mascara,
            )
        )

        print(
            f"({linha},{coluna}) "
            f"doce={resultado.percentual_doce:5.1f}% "
            f"area={resultado.area_doce}"
        )

    mosaico = gerar_mosaico(resultados)

    caminho_mosaico = (
        DIRETORIO_DEBUG / "mosaico_segmentacao.png"
    )

    cv2.imwrite(
        str(caminho_mosaico),
        mosaico,
    )

    print()
    print(f"Debug salvo em: {DIRETORIO_DEBUG}")
    print(f"Mosaico salvo em: {caminho_mosaico}")


if __name__ == "__main__":
    main()