from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


@dataclass(frozen=True)
class CaracteristicasCelula:
    linha: int
    coluna: int

    h_medio: float
    h_mediana: float
    h_dominante: float

    s_medio: float
    s_mediana: float
    s_desvio: float

    v_medio: float
    v_mediana: float
    v_desvio: float

    percentual_colorido: float


def extrair_caracteristicas(
    imagem: np.ndarray,
    linha: int,
    coluna: int,
) -> CaracteristicasCelula:

    if imagem is None:
        raise ValueError("Imagem inválida.")

    hsv = cv2.cvtColor(
        imagem,
        cv2.COLOR_BGR2HSV,
    )

    h = hsv[:, :, 0].astype(np.float32)
    s = hsv[:, :, 1].astype(np.float32)
    v = hsv[:, :, 2].astype(np.float32)

    # Ignora pixels muito pouco saturados.
    mascara_colorido = s > 50

    h_colorido = h[mascara_colorido]
    s_colorido = s[mascara_colorido]
    v_colorido = v[mascara_colorido]

    if h_colorido.size == 0:
        h_colorido = h.reshape(-1)
        s_colorido = s.reshape(-1)
        v_colorido = v.reshape(-1)

    # Histograma de matiz.
    histograma, _ = np.histogram(
        h_colorido,
        bins=180,
        range=(0, 180),
    )

    h_dominante = float(
        np.argmax(histograma)
    )

    percentual_colorido = (
        float(np.count_nonzero(mascara_colorido))
        / mascara_colorido.size
        * 100.0
    )

    return CaracteristicasCelula(
        linha=linha,
        coluna=coluna,

        h_medio=float(np.mean(h_colorido)),
        h_mediana=float(np.median(h_colorido)),
        h_dominante=h_dominante,

        s_medio=float(np.mean(s_colorido)),
        s_mediana=float(np.median(s_colorido)),
        s_desvio=float(np.std(s_colorido)),

        v_medio=float(np.mean(v_colorido)),
        v_mediana=float(np.median(v_colorido)),
        v_desvio=float(np.std(v_colorido)),

        percentual_colorido=percentual_colorido,
    )


def carregar_celulas(
    diretorio: Path,
) -> list[tuple[int, int, Path]]:

    if not diretorio.exists():
        raise FileNotFoundError(
            f"Diretório não encontrado: {diretorio}"
        )

    resultado = []

    for arquivo in sorted(
        diretorio.glob("*.png")
    ):
        try:
            nome = arquivo.stem
            linha, coluna = (
                map(int, nome.split("_"))
            )
        except ValueError:
            continue

        resultado.append(
            (
                linha,
                coluna,
                arquivo,
            )
        )

    return resultado


def main() -> None:

    diretorio = Path(
        "imagens_teste/celulas"
    )

    celulas = carregar_celulas(
        diretorio
    )

    if not celulas:
        raise RuntimeError(
            "Nenhuma célula encontrada."
        )

    print(
        f"Células encontradas: {len(celulas)}"
    )
    print()

    resultados = []

    for linha, coluna, caminho in celulas:

        imagem = cv2.imread(
            str(caminho)
        )

        if imagem is None:
            print(
                f"[ERRO] {caminho}"
            )
            continue

        caracteristicas = (
            extrair_caracteristicas(
                imagem,
                linha,
                coluna,
            )
        )

        resultados.append(
            caracteristicas
        )

        print(
            f"({linha},{coluna}) "
            f"H={caracteristicas.h_dominante:5.1f} "
            f"Hmed={caracteristicas.h_medio:6.1f} "
            f"S={caracteristicas.s_medio:6.1f} "
            f"Smed={caracteristicas.s_mediana:6.1f} "
            f"Sstd={caracteristicas.s_desvio:6.1f} "
            f"V={caracteristicas.v_medio:6.1f} "
            f"Vmed={caracteristicas.v_mediana:6.1f} "
            f"Vstd={caracteristicas.v_desvio:6.1f} "
            f"colorido="
            f"{caracteristicas.percentual_colorido:5.1f}%"
        )

    print()
    print(
        f"Características extraídas: "
        f"{len(resultados)}"
    )


if __name__ == "__main__":
    main()