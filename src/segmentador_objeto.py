from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(frozen=True)
class ResultadoSegmentacao:
    mascara: np.ndarray
    area_objeto: int
    percentual_objeto: float
    centro_x: float
    centro_y: float


def segmentar_objeto(
    imagem: np.ndarray,
) -> ResultadoSegmentacao:

    if imagem is None:
        raise ValueError("Imagem inválida.")

    altura, largura = imagem.shape[:2]

    hsv = cv2.cvtColor(
        imagem,
        cv2.COLOR_BGR2HSV,
    )

    h, s, v = cv2.split(hsv)

    # O fundo tende a possuir características
    # diferentes do objeto central.
    #
    # Começamos com saturação como primeiro filtro.
    mascara = np.where(
        s > 70,
        255,
        0,
    ).astype(np.uint8)

    # Remove pequenos ruídos.
    kernel = np.ones(
        (3, 3),
        dtype=np.uint8,
    )

    mascara = cv2.morphologyEx(
        mascara,
        cv2.MORPH_OPEN,
        kernel,
    )

    mascara = cv2.morphologyEx(
        mascara,
        cv2.MORPH_CLOSE,
        kernel,
    )

    # Procura componentes conectados.
    quantidade, labels, stats, centroides = (
        cv2.connectedComponentsWithStats(
            mascara,
            connectivity=8,
        )
    )

    if quantidade <= 1:
        return ResultadoSegmentacao(
            mascara=mascara,
            area_objeto=0,
            percentual_objeto=0.0,
            centro_x=largura / 2,
            centro_y=altura / 2,
        )

    # Ignora o componente 0, que é o fundo.
    melhor_indice = 1
    melhor_area = stats[1, cv2.CC_STAT_AREA]

    for indice in range(
        2,
        quantidade,
    ):
        area = stats[
            indice,
            cv2.CC_STAT_AREA,
        ]

        if area > melhor_area:
            melhor_area = area
            melhor_indice = indice

    mascara_objeto = np.where(
        labels == melhor_indice,
        255,
        0,
    ).astype(np.uint8)

    area_total = altura * largura

    percentual = (
        melhor_area
        / area_total
        * 100.0
    )

    centro_x, centro_y = centroides[
        melhor_indice
    ]

    return ResultadoSegmentacao(
        mascara=mascara_objeto,
        area_objeto=int(melhor_area),
        percentual_objeto=float(percentual),
        centro_x=float(centro_x),
        centro_y=float(centro_y),
    )