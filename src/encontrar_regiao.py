"""
Calibração ÚNICA da região do tabuleiro na tela.

Rode isso UMA VEZ (não em todo jogo). Ele te dá os números pra colar
como REGIAO_TELA em executar_bot.py. Só precisa rodar de novo se você
mudar a posição ou o tamanho da janela do jogo.

Uso:
    python src/encontrar_regiao.py
"""
from __future__ import annotations
import time
import pyautogui

try:
    import winsound

    def _beep(vezes: int = 1) -> None:
        for _ in range(vezes):
            winsound.Beep(880, 150)
            time.sleep(0.15)
except ImportError:
    def _beep(vezes: int = 1) -> None:
        pass


def main() -> None:
    print("=== CALIBRAÇÃO ÚNICA DA REGIÃO DO TABULEIRO ===")
    print("Deixe o jogo aberto e visível agora.")
    print("Começando em 5 segundos...")
    time.sleep(5)

    while True:
        _beep(1)  # mova até o canto superior esquerdo
        time.sleep(4)
        x1, y1 = pyautogui.position()

        _beep(2)  # mova até o canto inferior direito
        time.sleep(4)
        x2, y2 = pyautogui.position()

        if (x1, y1) == (x2, y2):
            _beep(4)
            print("Pontos iguais, repetindo...")
            time.sleep(2)
            continue

        break

    esq_x, esq_y = min(x1, x2), min(y1, y2)
    largura = abs(x2 - x1)
    altura = abs(y2 - y1)

    _beep(3)
    print("\n=== COLE ISTO em executar_bot.py, substituindo REGIAO_TELA ===\n")
    print(f"REGIAO_TELA = {{'left': {esq_x}, 'top': {esq_y}, 'width': {largura}, 'height': {altura}}}")


if __name__ == "__main__":
    main()