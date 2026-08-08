"""
Calibra automaticamente as categorias de cor do classificador usando
imagens de referência (uma por doce/cor), em vez de valores chutados na mão.

Uso:
    1. Coloque este arquivo em src/ (ao lado de modelo.py, classificador_cor.py etc).
    2. Confirme que imagens_teste/imagem_doces/ tem os arquivos:
           Red.webp, Yellow.webp, Green.webp, Blue.webp, Purple.webp, Orange.webp
    3. Rode a partir da RAIZ do repositório (mesmo diretório onde fica imagens_teste/):
           python src/calibrar_categorias.py
    4. Copie o bloco impresso no final para dentro de classificador_cor.py,
       substituindo CATEGORIAS e MAPEAMENTO.
"""
from __future__ import annotations
from pathlib import Path
import cv2
import numpy as np

from modelo import TipoPeca

DIRETORIO = Path("imagens_teste/imagem_doces")

# nome do arquivo (como está na pasta) -> TipoPeca correspondente
ARQUIVOS = {
    "Red.webp": TipoPeca.VERMELHO,
    "Yellow.webp": TipoPeca.AMARELO,
    "Green.webp": TipoPeca.VERDE,
    "Blue.webp": TipoPeca.AZUL,
    "Purple.webp": TipoPeca.ROXO,
    "Orange.webp": TipoPeca.LARANJA,
}


def analisar_doce(caminho: Path) -> tuple[float, float, float]:
    """
    Carrega a imagem PRESERVANDO o canal alfa (se houver) e calcula
    matiz dominante / saturação média / brilho médio usando só os
    pixels do doce (pixels transparentes ou de fundo são ignorados).
    """
    imagem = cv2.imread(str(caminho), cv2.IMREAD_UNCHANGED)
    if imagem is None:
        raise FileNotFoundError(f"Não consegui abrir: {caminho}")

    if imagem.ndim == 3 and imagem.shape[2] == 4:
        # Tem canal alfa: usa como máscara -> mantém só pixels visíveis.
        bgr = imagem[:, :, :3]
        alfa = imagem[:, :, 3]
        mascara = alfa > 10
    else:
        # Sem canal alfa: assume fundo sólido claro/escuro e descarta
        # pixels quase pretos ou quase brancos (prováveis bordas/fundo).
        bgr = imagem[:, :, :3] if imagem.ndim == 3 else cv2.cvtColor(imagem, cv2.COLOR_GRAY2BGR)
        cinza = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        mascara = (cinza > 15) & (cinza < 240)

    if mascara.sum() < 20:
        raise RuntimeError(
            f"Máscara ficou vazia demais em {caminho} — confira a imagem "
            f"(pode ser toda transparente, toda preta ou toda branca)."
        )

    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    h = hsv[:, :, 0][mascara]
    s = hsv[:, :, 1][mascara]
    v = hsv[:, :, 2][mascara]

    hist = np.bincount(h.astype(int), minlength=180)
    matiz_dominante = float(np.argmax(hist))
    saturacao = float(np.mean(s))
    brilho = float(np.mean(v))

    return matiz_dominante, saturacao, brilho


def main() -> None:
    resultados: dict[str, tuple[float, float, float]] = {}

    print("=== ANALISANDO IMAGENS DE REFERÊNCIA ===\n")

    for nome_arquivo, tipo in ARQUIVOS.items():
        caminho = DIRETORIO / nome_arquivo
        matiz, sat, bri = analisar_doce(caminho)
        resultados[tipo.name] = (matiz, sat, bri)
        print(
            f"{nome_arquivo:15s} -> {tipo.name:10s}  "
            f"matiz={matiz:6.2f}  saturacao={sat:6.2f}  brilho={bri:6.2f}"
        )

    print("\n\n# ---- Cole isto em classificador_cor.py, substituindo CATEGORIAS e MAPEAMENTO ----\n")

    print("    CATEGORIAS = (")
    for nome_tipo, (matiz, sat, bri) in resultados.items():
        grupo = nome_tipo.lower()
        print(
            f'        CategoriaCor(nome="{grupo}", matiz={matiz:.2f}, '
            f'saturacao={sat:.2f}, brilho={bri:.2f}),'
        )
    print("    )\n")

    print("    MAPEAMENTO = {")
    for nome_tipo in resultados:
        grupo = nome_tipo.lower()
        print(f'        "{grupo}": TipoPeca.{nome_tipo},')
    print("    }")


if __name__ == "__main__":
    main()