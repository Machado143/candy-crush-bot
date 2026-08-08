from src.classificador_cor import ClassificadorCor


def test_grupo_0():
    classificador = ClassificadorCor()

    resultado = classificador.classificar(
        matiz=1.0,
        saturacao=138.76,
        brilho=222.94,
    )

    assert resultado.categoria == "grupo_0"


def test_grupo_1():
    classificador = ClassificadorCor()

    resultado = classificador.classificar(
        matiz=55.0,
        saturacao=181.58,
        brilho=168.27,
    )

    assert resultado.categoria == "grupo_1"


def test_grupo_2():
    classificador = ClassificadorCor()

    resultado = classificador.classificar(
        matiz=96.69,
        saturacao=140.45,
        brilho=197.46,
    )

    assert resultado.categoria == "grupo_2"


def test_grupo_3():
    classificador = ClassificadorCor()

    resultado = classificador.classificar(
        matiz=107.0,
        saturacao=144.98,
        brilho=240.04,
    )

    assert resultado.categoria == "grupo_3"


def test_grupo_4():
    classificador = ClassificadorCor()

    resultado = classificador.classificar(
        matiz=144.57,
        saturacao=164.89,
        brilho=240.48,
    )

    assert resultado.categoria == "grupo_4"


def test_matiz_circular():
    classificador = ClassificadorCor()

    resultado = classificador.classificar(
        matiz=179.0,
        saturacao=138.76,
        brilho=222.94,
    )

    assert resultado.categoria == "grupo_0"