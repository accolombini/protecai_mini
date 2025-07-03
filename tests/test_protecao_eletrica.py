import pytest
from infra.protecao.protecao_eletrica import (
    Rele51, Rele67, Rele87T, Rele27, Rele59, Disjuntor, ProtecaoEletrica
)


def test_rele51_atuacao():
    """
    Testa a atuação do relé de sobrecorrente Rele51.
    Deve atuar quando a corrente medida for maior ou igual à corrente de disparo.
    """
    rele = Rele51(nome="51-1", barra_origem=1, corrente_disparo=100.0)
    assert rele.atuar(120.0) is True
    assert rele.atuar(80.0) is False


def test_rele67_atuacao():
    """
    Testa a atuação do relé direcional Rele67.
    Deve atuar somente se a corrente for suficiente e a direção coincidir.
    """
    rele = Rele67(nome="67-1", barra_origem=1,
                  corrente_disparo=90.0, direcao="ida")
    assert rele.atuar(100.0, "ida") is True
    assert rele.atuar(100.0, "volta") is False
    assert rele.atuar(80.0, "ida") is False


def test_rele87t_atuacao():
    """
    Testa a atuação do relé diferencial Rele87T.
    Atua se a diferença entre corrente primária e secundária for superior ao limiar.
    """
    rele = Rele87T(nome="87T-1", barra_origem=1,
                   corrente_disparo=50.0,
                   corrente_secundario=45.0,
                   transformador_id="TR1")
    # O método atuar do Rele87T recebe apenas corrente_primario
    assert rele.atuar(100.0) is True  # |100 - 45| = 55 >= 50
    assert rele.atuar(70.0) is False  # |70 - 45| = 25 < 50


def test_rele27_e_59_atuacao():
    """
    Testa os relés de subtensão (27) e sobretensão (59).
    Cada um deve atuar conforme os limiares configurados.
    """
    # Para Rele27 e Rele59, corrente_disparo representa o limiar de tensão
    rele27 = Rele27(nome="27-1", barra_origem=1, corrente_disparo=0.85)  # tensão mínima
    rele59 = Rele59(nome="59-1", barra_origem=1, corrente_disparo=1.10)  # tensão máxima

    assert rele27.atuar(0.80) is True  # 0.80 <= 0.85
    assert rele27.atuar(0.90) is False  # 0.90 > 0.85
    assert rele59.atuar(1.15) is True  # 1.15 >= 1.10
    assert rele59.atuar(1.05) is False  # 1.05 < 1.10


def test_disjuntor_abrir():
    """
    Testa a funcionalidade de abertura do disjuntor.
    """
    dj = Disjuntor(nome="DJ-1", barra_origem=1)
    assert dj.status == "fechado"  # Estado inicial
    dj.abrir()
    assert dj.status == "aberto"
    assert dj.esta_aberto() is True
