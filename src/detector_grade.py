from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from geometria_grade import GeometriaGrade


class DetectorGrade:
    """
    Detecta uma grade 7x7 usando perfis de gradiente
    da imagem do tabuleiro.
    """

    VERSAO = "geometria-v2"

    def detectar(
        self,
        imagem: np.ndarray,
        linhas: int = 7,
        colunas: int = 7,
    ) -> GeometriaGrade:

        if imagem is None:
            raise ValueError("Imagem inválida.")

        if linhas < 1 or colunas < 1:
            raise ValueError(
                "Linhas e colunas devem ser maiores que zero."
            )

        cinza = cv2.cvtColor(
            imagem,
            cv2.COLOR_BGR2GRAY,
        )

        # Suavização leve para reduzir ruído.
        cinza = cv2.GaussianBlur(
            cinza,
            (5, 5),
            0,
        )

        # Gradiente X:
        # detecta mudanças verticais.
        grad_x = cv2.Sobel(
            cinza,
            cv2.CV_64F,
            1,
            0,
            ksize=3,
        )

        grad_x = np.abs(grad_x)

        perfil_x = np.mean(
            grad_x,
            axis=0,
        )

        # Gradiente Y:
        # detecta mudanças horizontais.
        grad_y = cv2.Sobel(
            cinza,
            cv2.CV_64F,
            0,
            1,
            ksize=3,
        )

        grad_y = np.abs(grad_y)

        perfil_y = np.mean(
            grad_y,
            axis=1,
        )

        limites_x = self._detectar_limites(
            perfil_x,
            quantidade=colunas + 1,
        )

        limites_y = self._detectar_limites(
            perfil_y,
            quantidade=linhas + 1,
        )

        if limites_x is None:
            raise RuntimeError(
                "Não foi possível detectar "
                "os limites das colunas."
            )

        if limites_y is None:
            raise RuntimeError(
                "Não foi possível detectar "
                "os limites das linhas."
            )

        return GeometriaGrade(
            limites_x=tuple(limites_x),
            limites_y=tuple(limites_y),
        )

    def _detectar_limites(
        self,
        perfil: np.ndarray,
        quantidade: int,
    ) -> list[int] | None:

        if perfil.size == 0:
            return None

        # Suaviza o perfil.
        kernel = np.ones(
            9,
            dtype=np.float64,
        )

        perfil_suave = np.convolve(
            perfil,
            kernel / kernel.size,
            mode="same",
        )

        # Procuramos picos locais.
        candidatos = self._encontrar_picos(
            perfil_suave
        )

        if len(candidatos) < quantidade:
            return None

        # Procuramos a sequência mais regular
        # entre os candidatos.
        melhor = self._melhor_sequencia(
            candidatos,
            perfil_suave,
            quantidade,
        )

        return melhor

    def _encontrar_picos(
        self,
        perfil: np.ndarray,
    ) -> list[int]:

        maior = float(
            np.max(perfil)
        )

        if maior <= 0:
            return []

        # Consideramos apenas regiões
        # relativamente fortes.
        threshold = maior * 0.35

        candidatos: list[int] = []

        for i in range(
            1,
            len(perfil) - 1,
        ):

            atual = perfil[i]

            if atual < threshold:
                continue

            if (
                atual >= perfil[i - 1]
                and atual >= perfil[i + 1]
            ):
                candidatos.append(i)

        # Agrupa picos muito próximos.
        agrupados: list[int] = []

        for ponto in candidatos:

            if not agrupados:
                agrupados.append(ponto)
                continue

            if ponto - agrupados[-1] <= 12:

                anterior = agrupados[-1]

                if perfil[ponto] > perfil[anterior]:
                    agrupados[-1] = ponto

            else:
                agrupados.append(ponto)

        return agrupados

    def _melhor_sequencia(
        self,
        candidatos: list[int],
        perfil: np.ndarray,
        quantidade: int,
    ) -> list[int] | None:

        melhor: list[int] | None = None
        melhor_score = float("inf")

        if len(candidatos) < quantidade:
            return None

        # Testa cada candidato como possível
        # primeiro limite.
        for inicio in range(
            len(candidatos)
        ):

            primeiro = candidatos[inicio]

            # Precisamos de quantidade-1 pontos
            # depois do primeiro.
            restantes = candidatos[
                inicio + 1:
            ]

            if len(restantes) < quantidade - 1:
                continue

            # Estimamos um tamanho de célula
            # entre aproximadamente 50 e 100 px.
            for ultimo in restantes:

                distancia_total = (
                    ultimo - primeiro
                )

                if distancia_total <= 0:
                    continue

                tamanho = (
                    distancia_total
                    / (quantidade - 1)
                )

                if not 50 <= tamanho <= 100:
                    continue

                selecionados = [
                    primeiro
                ]

                erro_posicao = 0.0

                usados = {
                    primeiro
                }

                for indice in range(
                    1,
                    quantidade,
                ):

                    esperado = (
                        primeiro
                        + indice * tamanho
                    )

                    candidato = min(
                        restantes,
                        key=lambda ponto: abs(
                            ponto - esperado
                        ),
                    )

                    if candidato in usados:
                        break

                    erro_posicao += abs(
                        candidato - esperado
                    )

                    selecionados.append(
                        candidato
                    )

                    usados.add(candidato)

                if len(
                    selecionados
                ) != quantidade:
                    continue

                # Calcula o espaçamento real.
                espacamentos = np.diff(
                    selecionados
                )

                if np.any(
                    espacamentos <= 0
                ):
                    continue

                media = float(
                    np.mean(espacamentos)
                )

                desvio = float(
                    np.std(espacamentos)
                )

                # Quanto maior a força dos picos,
                # melhor.
                forca_picos = sum(
                    float(perfil[ponto])
                    for ponto in selecionados
                )

                # Normaliza a força para entrar
                # no score sem dominar completamente.
                media_forca = (
                    forca_picos
                    / quantidade
                )

                if media_forca <= 0:
                    continue

                score = (
                    erro_posicao
                    + desvio * 3
                    - media_forca * 0.05
                )

                if score < melhor_score:
                    melhor_score = score
                    melhor = selecionados

        return melhor


def desenhar_debug(
    imagem: np.ndarray,
    grade: GeometriaGrade,
) -> np.ndarray:

    debug = imagem.copy()

    # Desenha cada uma das 49 células.
    for linha in range(
        grade.linhas
    ):

        for coluna in range(
            grade.colunas
        ):

            x1, y1, x2, y2 = (
                grade.limites(
                    linha,
                    coluna,
                )
            )

            centro_x, centro_y = (
                grade.centro(
                    linha,
                    coluna,
                )
            )

            # Retângulo da célula.
            cv2.rectangle(
                debug,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2,
            )

            # Centro.
            cv2.circle(
                debug,
                (
                    centro_x,
                    centro_y,
                ),
                4,
                (0, 0, 255),
                -1,
            )

            # Coordenada.
            cv2.putText(
                debug,
                f"{linha},{coluna}",
                (
                    x1 + 4,
                    y1 + 16,
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

    return debug


def main() -> None:

    caminho = Path(
        "imagens_teste/tabuleiro.png"
    )

    imagem = cv2.imread(
        str(caminho)
    )

    if imagem is None:
        raise FileNotFoundError(
            f"Imagem não encontrada: {caminho}"
        )

    print(
        f"Imagem: "
        f"{imagem.shape[1]}x"
        f"{imagem.shape[0]}"
    )

    detector = DetectorGrade()

    print(
        "Detector:",
        DetectorGrade.VERSAO,
    )

    grade = detector.detectar(
        imagem,
        linhas=7,
        colunas=7,
    )

    print()
    print("=== GRADE DETECTADA ===")

    print(
        f"Linhas: {grade.linhas}"
    )

    print(
        f"Colunas: {grade.colunas}"
    )

    print(
        "Limites X:",
        grade.limites_x,
    )

    print(
        "Limites Y:",
        grade.limites_y,
    )

    print()
    print("Células:")

    for linha in range(
        grade.linhas
    ):

        for coluna in range(
            grade.colunas
        ):

            limites = grade.limites(
                linha,
                coluna,
            )

            centro = grade.centro(
                linha,
                coluna,
            )

            print(
                f"({linha},{coluna}) "
                f"limites={limites} "
                f"centro={centro}"
            )

    debug = desenhar_debug(
        imagem,
        grade,
    )

    saida = Path(
        "imagens_teste/debug_grade.png"
    )

    cv2.imwrite(
        str(saida),
        debug,
    )

    print()
    print(
        f"Debug salvo em: {saida}"
    )


if __name__ == "__main__":
    main()