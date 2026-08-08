from __future__ import annotations
import time
import cv2
import numpy as np
import mss
import pyautogui

from detector_grade import DetectorGrade
from extrator_celulas import ExtratorCelulas
from visao import Visao
from classificador_cor import ClassificadorCor
from modelo import Tabuleiro, Peca
from solver import melhor_jogada

# Região fixa da tela onde o tabuleiro fica. Gerada com
# src/encontrar_regiao.py — só muda se a janela do jogo mudar de
# posição/tamanho. SUBSTITUA pelos valores que o encontrar_regiao.py
# imprimiu pra você.
REGIAO_TELA = {'left': 724, 'top': 301, 'width': 463, 'height': 524}

def capturar_tabuleiro() -> np.ndarray:
    with mss.mss() as sct:
        captura = np.array(sct.grab(REGIAO_TELA))
    return cv2.cvtColor(captura, cv2.COLOR_BGRA2BGR)


def main() -> None:
    print("=== BOT CANDY CRUSH ===")
    print("Alt-tab pro jogo agora. Capturando em 3 segundos...")
    time.sleep(3)

    # 1. Captura a tela AO VIVO na região do tabuleiro
    imagem_base = capturar_tabuleiro()

    # 2. Detecta a grade e extrai as células
    detector = DetectorGrade()
    grade = detector.detectar(imagem_base, linhas=7, colunas=7)
    print("Grade detectada com sucesso.")

    extrator = ExtratorCelulas()
    celulas_imagens = extrator.extrair(imagem_base, grade)

    # 3. Classifica as cores
    visao = Visao()
    classificador = ClassificadorCor()
    tabuleiro = Tabuleiro(7, 7)

    for linha in range(7):
        for coluna in range(7):
            img_celula = celulas_imagens[(linha, coluna)]
            caract = visao.analisar(img_celula, linha, coluna)
            resultado = classificador.classificar(
                matiz=caract.matiz_dominante,
                saturacao=caract.saturacao,
                brilho=caract.brilho
            )
            peca = Peca(tipo=resultado.tipo_peca, linha=linha, coluna=coluna)
            tabuleiro.definir(linha, coluna, peca)

    print("\nTabuleiro montado:")
    print(tabuleiro)

    # 4. Encontra a melhor jogada
    jogada = melhor_jogada(tabuleiro)
    if jogada is None:
        print("Nenhuma jogada válida encontrada.")
        return

    print(f"\nMelhor jogada: {jogada}")

    # 5. Coordenadas relativas à captura -> absolutas da tela.
    #    Sem escala nenhuma: a captura JÁ é a tela real em pixels reais,
    #    então só soma o offset da região.
    cx1, cy1 = grade.centro(jogada.l1, jogada.c1)
    cx2, cy2 = grade.centro(jogada.l2, jogada.c2)

    x_tela1 = REGIAO_TELA["left"] + cx1
    y_tela1 = REGIAO_TELA["top"] + cy1
    x_tela2 = REGIAO_TELA["left"] + cx2
    y_tela2 = REGIAO_TELA["top"] + cy2

    print(f"\nCoordenadas na tela: ({x_tela1}, {y_tela1}) -> ({x_tela2}, {y_tela2})")

    # 6. Executa o arraste
    try:
        pyautogui.moveTo(x_tela1, y_tela1, duration=0.3)
        pyautogui.mouseDown()
        time.sleep(0.2)
        pyautogui.moveTo(x_tela2, y_tela2, duration=0.4)
        time.sleep(0.2)
        pyautogui.mouseUp()
        print("Jogada executada com sucesso!")
    except Exception as e:
        print(f"Erro ao tentar clicar: {e}")


if __name__ == "__main__":
    main()