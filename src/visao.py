from __future__ import annotations
from dataclasses import dataclass
import cv2
import numpy as np
from segmentador_doce import SegmentadorDoce

@dataclass(frozen=True)
class CaracteristicasCelula:
    linha: int
    coluna: int
    azul_medio: float
    verde_medio: float
    vermelho_medio: float
    matiz: float
    saturacao: float
    brilho: float
    matiz_dominante: float

class Visao:
    def __init__(self):
        self.segmentador = SegmentadorDoce(
            saturacao_minima=70,
            brilho_minimo=50,
            area_minima=20
        )

    def analisar(self, imagem: np.ndarray, linha: int, coluna: int) -> CaracteristicasCelula:
        if imagem is None or imagem.size == 0:
            raise ValueError("Imagem da célula inválida.")

        # 1. Segmenta o doce para pegar só a cor real
        resultado_seg = self.segmentador.segmentar(imagem)
        mascara = resultado_seg.mascara

        hsv = cv2.cvtColor(imagem, cv2.COLOR_BGR2HSV)

        # Se tiver doce, usamos apenas os pixels do doce para calcular a cor
        if resultado_seg.area_doce > 20:
            h = hsv[:, :, 0][mascara > 0]
            s = hsv[:, :, 1][mascara > 0]
            v = hsv[:, :, 2][mascara > 0]
        else:
            h = hsv[:, :, 0].reshape(-1)
            s = hsv[:, :, 1].reshape(-1)
            v = hsv[:, :, 2].reshape(-1)

        matiz = float(np.mean(h))
        saturacao = float(np.mean(s))
        brilho = float(np.mean(v))

        # Matiz dominante
        hist = np.bincount(h.astype(int), minlength=180)
        matiz_dominante = float(np.argmax(hist))

        bgr_medio = np.mean(imagem, axis=(0, 1))
        return CaracteristicasCelula(
            linha=linha,
            coluna=coluna,
            azul_medio=float(bgr_medio[0]),
            verde_medio=float(bgr_medio[1]),
            vermelho_medio=float(bgr_medio[2]),
            matiz=matiz,
            saturacao=saturacao,
            brilho=brilho,
            matiz_dominante=matiz_dominante
        )

def carregar_celulas(diretorio: str = "imagens_teste/celulas") -> list[CaracteristicasCelula]:
    visao = Visao()
    resultados = []
    for linha in range(7):
        for coluna in range(7):
            caminho = f"{diretorio}/{linha:02d}_{coluna:02d}.png"
            imagem = cv2.imread(caminho)
            if imagem is None:
                raise FileNotFoundError(f"Célula não encontrada: {caminho}")
            resultados.append(visao.analisar(imagem, linha, coluna))
    return resultados