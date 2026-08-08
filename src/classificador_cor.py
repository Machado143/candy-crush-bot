from __future__ import annotations
from dataclasses import dataclass
from modelo import TipoPeca

@dataclass(frozen=True)
class CategoriaCor:
    nome: str
    matiz: float
    saturacao: float
    brilho: float

@dataclass(frozen=True)
class ResultadoClassificacao:
    categoria: str
    distancia: float
    confianca: float
    tipo_peca: TipoPeca

class ClassificadorCor:
    CATEGORIAS = (
        CategoriaCor(nome="grupo_0", matiz=1.0,   saturacao=138.76, brilho=222.94),
        CategoriaCor(nome="grupo_1", matiz=55.0,  saturacao=181.58, brilho=168.27),
        CategoriaCor(nome="grupo_2", matiz=96.69, saturacao=140.45, brilho=197.46),
        CategoriaCor(nome="grupo_3", matiz=107.0, saturacao=144.98, brilho=240.04),
        CategoriaCor(nome="grupo_4", matiz=144.57, saturacao=164.89, brilho=240.48),
    )

    # 👇 AQUI VOCÊ PODE AJUSTAR SE AS CORES NÃO BATEM COM O JOGO
    MAPEAMENTO = {
        "grupo_0": TipoPeca.ROXO,
        "grupo_1": TipoPeca.VERMELHO,
        "grupo_2": TipoPeca.AZUL,
        "grupo_3": TipoPeca.VERDE,
        "grupo_4": TipoPeca.LARANJA,
    }

    def classificar(self, matiz: float, saturacao: float, brilho: float) -> ResultadoClassificacao:
        melhor_categoria = None
        melhor_distancia = float("inf")

        for categoria in self.CATEGORIAS:
            diff_h = min(abs(matiz - categoria.matiz), 180.0 - abs(matiz - categoria.matiz))
            diff_s = abs(saturacao - categoria.saturacao)
            diff_v = abs(brilho - categoria.brilho)
            distancia = diff_h * 1.0 + diff_s * 0.20 + diff_v * 0.15

            if distancia < melhor_distancia:
                melhor_distancia = distancia
                melhor_categoria = categoria

        if melhor_categoria is None:
            raise RuntimeError("Nenhuma categoria disponível.")

        confianca = max(0.0, min(100.0, 100.0 / (1.0 + melhor_distancia)))
        tipo_peca = self.MAPEAMENTO[melhor_categoria.nome]

        return ResultadoClassificacao(
            categoria=melhor_categoria.nome,
            distancia=melhor_distancia,
            confianca=confianca,
            tipo_peca=tipo_peca
        )