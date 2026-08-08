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
        CategoriaCor(nome="vermelho", matiz=0.00, saturacao=254.12, brilho=180.49),
        CategoriaCor(nome="amarelo", matiz=22.00, saturacao=248.96, brilho=209.61),
        CategoriaCor(nome="verde", matiz=52.00, saturacao=243.06, brilho=142.46),
        CategoriaCor(nome="azul", matiz=105.00, saturacao=231.05, brilho=195.11),
        CategoriaCor(nome="roxo", matiz=142.00, saturacao=231.29, brilho=199.16),
        CategoriaCor(nome="laranja", matiz=16.00, saturacao=240.60, brilho=201.45),
        CategoriaCor(nome="maquina", matiz=96.00, saturacao=107.31, brilho=212.40),
    )

    MAPEAMENTO = {
        "vermelho": TipoPeca.VERMELHO,
        "amarelo": TipoPeca.AMARELO,
        "verde": TipoPeca.VERDE,
        "azul": TipoPeca.AZUL,
        "roxo": TipoPeca.ROXO,
        "laranja": TipoPeca.LARANJA,
        "maquina": TipoPeca.MAQUINA,
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