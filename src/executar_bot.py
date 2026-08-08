from __future__ import annotations
from pathlib import Path
import time
import cv2
import numpy as np
import pyautogui

from detector_grade import DetectorGrade
from extrator_celulas import ExtratorCelulas
from visao import Visao
from classificador_cor import ClassificadorCor
from modelo import Tabuleiro, Peca
from solver import melhor_jogada

CAMINHO_IMAGEM = Path("imagens_teste/tabuleiro.png")

def calibrar_posicao_tela() -> tuple[int, int, int, int]:
    """
    Abre uma janela para o usuário clicar no canto superior esquerdo e 
    inferior direito do tabuleiro, para mapear a posição exata na tela.
    """
    print("\n=== CALIBRAÇÃO ===")
    print("Vamos mapear onde o tabuleiro está na sua tela.")
    print("Você tem 5 segundos para abrir o jogo.")
    time.sleep(5)

    print("Clique no CANTO SUPERIOR ESQUERDO do tabuleiro (dentro da borda verde).")
    x1, y1 = pyautogui.position()
    print(f"Canto superior esquerdo capturado: ({x1}, {y1})")
    time.sleep(1)

    print("Clique no CANTO INFERIOR DIREITO do tabuleiro (dentro da borda verde).")
    x2, y2 = pyautogui.position()
    print(f"Canto inferior direito capturado: ({x2}, {y2})")

    return x1, y1, x2, y2

def main() -> None:
    print("=== BOT CANDY CRUSH ===")

    # 1. Carrega a imagem base para extrair as cores
    imagem_base = cv2.imread(str(CAMINHO_IMAGEM))
    if imagem_base is None:
        raise FileNotFoundError(f"Imagem não encontrada: {CAMINHO_IMAGEM}")

    # 2. Detecta a grade e extrai as células DA IMAGEM BASE
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

    # 5. Pega as coordenadas RELATIVAS à imagem base
    cx1, cy1 = grade.centro(jogada.l1, jogada.c1)
    cx2, cy2 = grade.centro(jogada.l2, jogada.c2)

    print(f"Coordenadas relativas: ({cx1}, {cy1}) e ({cx2}, {cy2})")

    # 6. Calibra a posição do tabuleiro na tela
    esq_x, esq_y, dir_x, dir_y = calibrar_posicao_tela()

    # A imagem base tem largura e altura. Calculamos a escala.
    img_h, img_w = imagem_base.shape[:2]
    largura_tela = dir_x - esq_x
    altura_tela = dir_y - esq_y

    # Calcula a posição exata na tela baseado na escala
    x_tela1 = int(esq_x + (cx1 / img_w) * largura_tela)
    y_tela1 = int(esq_y + (cy1 / img_h) * altura_tela)
    x_tela2 = int(esq_x + (cx2 / img_w) * largura_tela)
    y_tela2 = int(esq_y + (cy2 / img_h) * altura_tela)

    print(f"\nCoordenadas ajustadas para tela: ({x_tela1}, {y_tela1}) -> ({x_tela2}, {y_tela2})")

    # 7. EXECUTA O ARRASTE (Drag & Drop)
    print("\nPreparando para executar o arraste em 3 segundos...")
    time.sleep(3)

    try:
        # Move até a primeira peça, segura o botão
        pyautogui.moveTo(x_tela1, y_tela1, duration=0.3)
        pyautogui.mouseDown()
        time.sleep(0.2)

        # Arrasta até a segunda peça
        pyautogui.moveTo(x_tela2, y_tela2, duration=0.4)
        time.sleep(0.2)

        # Solta o botão
        pyautogui.mouseUp()
        print("Jogada executada com sucesso!")

    except Exception as e:
        print(f"Erro ao tentar clicar: {e}")

if __name__ == "__main__":
    main()