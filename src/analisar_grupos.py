from __future__ import annotations

from collections import defaultdict

from classificador_cor import ClassificadorCor
from visao import carregar_celulas


def main() -> None:
    resultados = carregar_celulas()

    classificador = ClassificadorCor()

    grupos = defaultdict(list)

    for celula in resultados:
        grupo = classificador.classificar(
            celula.matiz_dominante
        )

        grupos[grupo].append(celula)

    print("=== ANÁLISE DOS GRUPOS ===")

    for nome in sorted(grupos):

        celulas = grupos[nome]

        quantidade = len(celulas)

        media_h = sum(
            c.matiz
            for c in celulas
        ) / quantidade

        media_s = sum(
            c.saturacao
            for c in celulas
        ) / quantidade

        media_v = sum(
            c.brilho
            for c in celulas
        ) / quantidade

        media_hd = sum(
            c.matiz_dominante
            for c in celulas
        ) / quantidade

        print()
        print(nome)
        print(f"  quantidade: {quantidade}")
        print(f"  H médio: {media_h:.2f}")
        print(f"  S médio: {media_s:.2f}")
        print(f"  V médio: {media_v:.2f}")
        print(
            f"  H dominante médio: "
            f"{media_hd:.2f}"
        )

        print("  células:")

        for celula in celulas:
            print(
                f"    ({celula.linha},"
                f"{celula.coluna}) "
                f"H={celula.matiz_dominante:.0f} "
                f"S={celula.saturacao:.1f} "
                f"V={celula.brilho:.1f}"
            )


if __name__ == "__main__":
    main()