from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(frozen=True)
class ResultadoSegmentacao:
    mascara: np.ndarray
    percentual_doce: float
    area_doce: int


class SegmentadorDoce:
    """
    Segmenta regiões potencialmente pertencentes ao doce dentro de uma célula.

    A saída é uma máscara binária:
        0   -> fundo
        255 -> possível doce

    Esta etapa NÃO tenta identificar a cor do doce.
    """

    def __init__(
        self,
        saturacao_minima: int = 70,
        brilho_minimo: int = 50,
        kernel_tamanho: int = 3,
        area_minima: int = 20,
    ) -> None:
        self.saturacao_minima = saturacao_minima
        self.brilho_minimo = brilho_minimo
        self.kernel_tamanho = kernel_tamanho
        self.area_minima = area_minima

    def segmentar(self, imagem: np.ndarray) -> ResultadoSegmentacao:
        if imagem is None or imagem.size == 0:
            raise ValueError("Imagem da célula está vazia.")

        if imagem.ndim != 3 or imagem.shape[2] != 3:
            raise ValueError("A imagem deve estar no formato BGR.")

        hsv = cv2.cvtColor(imagem, cv2.COLOR_BGR2HSV)

        _, saturacao, brilho = cv2.split(hsv)

        # Regiões com alguma saturação e brilho suficiente.
        mascara = cv2.inRange(
            hsv,
            np.array(
                [
                    0,
                    self.saturacao_minima,
                    self.brilho_minimo,
                ],
                dtype=np.uint8,
            ),
            np.array(
                [
                    179,
                    255,
                    255,
                ],
                dtype=np.uint8,
            ),
        )

        # Remove pequenos ruídos e fecha pequenos buracos.
        kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE,
            (
                self.kernel_tamanho,
                self.kernel_tamanho,
            ),
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

        # Remove componentes muito pequenos.
        mascara = self._remover_componentes_pequenos(mascara)

        area_total = mascara.shape[0] * mascara.shape[1]
        area_doce = int(cv2.countNonZero(mascara))

        percentual = (
            (area_doce / area_total) * 100
            if area_total > 0
            else 0.0
        )

        return ResultadoSegmentacao(
            mascara=mascara,
            percentual_doce=percentual,
            area_doce=area_doce,
        )

    def _remover_componentes_pequenos(
        self,
        mascara: np.ndarray,
    ) -> np.ndarray:
        quantidade, labels, estatisticas, _ = cv2.connectedComponentsWithStats(
            mascara,
            connectivity=8,
        )

        resultado = np.zeros_like(mascara)

        for indice in range(1, quantidade):
            area = estatisticas[indice, cv2.CC_STAT_AREA]

            if area >= self.area_minima:
                resultado[labels == indice] = 255

        return resultado