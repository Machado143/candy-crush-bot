from __future__ import annotations

import pytest

from src.visao import CaracteristicasCelula, classificar_tabuleiro


class _ResultadoFake:
    def __init__(self, categoria: str) -> None:
        self.categoria = categoria


class _ClassificadorFake:
    def classificar(self, matiz: float, saturacao: float, brilho: float) -> _ResultadoFake:
        categoria = f"cat_{int(matiz)}_{int(saturacao)}_{int(brilho)}"
        return _ResultadoFake(categoria)


def test_classificar_tabuleiro_usa_resultado_do_classificador(monkeypatch: pytest.MonkeyPatch) -> None:
    import classificador_cor

    monkeypatch.setattr(classificador_cor, "ClassificadorCor", _ClassificadorFake)

    resultados = [
        CaracteristicasCelula(
            linha=linha,
            coluna=coluna,
            azul_medio=0.0,
            verde_medio=0.0,
            vermelho_medio=0.0,
            matiz=float(linha * 10 + coluna),
            saturacao=float(100 + coluna),
            brilho=float(200 + linha),
        )
        for linha in range(7)
        for coluna in range(7)
    ]

    tabuleiro = classificar_tabuleiro(resultados)

    assert len(tabuleiro) == 7
    assert all(len(linha) == 7 for linha in tabuleiro)
    assert tabuleiro[0][0] == "cat_0_100_200"
    assert tabuleiro[6][6] == "cat_66_106_206"
