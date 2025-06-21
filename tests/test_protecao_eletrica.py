import pytest
from infra.protecao.protecao_eletrica import (
    Rele51, Rele67, Rele87T, Rele27, Rele59, Disjuntor, ProtecaoEletrica
)


def test_rele51_atuacao():
    """
    Testa a atuação do relé de sobrecorrente Rele51.

    O relé deve atuar quando a corrente medida for maior ou igual à corrente de disparo.
    """
    rele = Rele51(nome="51-1", barra_origem=1, corrente_disparo=100.0)
    assert rele.atuar(120.0) is True
    assert rele.atuar(80.0) is False


def test_rele67_atuacao():
    """
    Testa a atuação do relé direcional Rele67.

    O relé deve atuar apenas se:
    - A corrente for maior ou igual ao limiar de disparo
    - A direção do fluxo coincidir com a direção configurada no relé
    """
    rele = Rele67(nome="67-1", barra_origem=1,
                  corrente_disparo=90.0, direcao="ida")
    assert rele.atuar(100.0, "ida") is True
    assert rele.atuar(100.0, "volta") is False
    assert rele.atuar(80.0, "ida") is False


def test_rele87t_atuacao():
    """
    Testa a atuação do relé diferencial de transformador Rele87T.

    A atuação ocorre se a diferença entre as correntes primária e secundária
    for maior ou igual à corrente de disparo.
    """
    rele = Rele87T(
        nome="87T-1", barra_origem=1, corrente_disparo=10.0,
        corrente_secundario=90.0, transformador_id="TR1"
    )
    assert rele.atuar(105.0) is True
    assert rele.atuar(95.0) is False


def test_rele27_atuacao():
    """
    Testa a atuação do relé de subtensão Rele27.

    A atuação ocorre quando a tensão é menor ou igual ao valor de disparo.
    """
    rele = Rele27(nome="27-1", barra_origem=1, corrente_disparo=95.0)
    assert rele.atuar(90.0) is True
    assert rele.atuar(100.0) is False


def test_rele59_atuacao():
    """
    Testa a atuação do relé de sobretensão Rele59.

    A atuação ocorre quando a tensão é maior ou igual ao valor de disparo.
    """
    rele = Rele59(nome="59-1", barra_origem=1, corrente_disparo=105.0)
    assert rele.atuar(110.0) is True
    assert rele.atuar(100.0) is False


def test_disjuntor_operacao():
    """
    Testa a operação do disjuntor:
    - Verifica abertura e fechamento manual
    - Verifica atuação automática
    - Verifica o status antes e depois das ações
    """
    disjuntor = Disjuntor(nome="DJ-1", barra_origem=1)

    # Estado inicial
    assert disjuntor.status == "fechado"
    assert disjuntor.esta_aberto() is False

    # Abertura manual
    disjuntor.abrir()
    assert disjuntor.status == "aberto"
    assert disjuntor.esta_aberto() is True

    # Fechamento manual
    disjuntor.fechar()
    assert disjuntor.status == "fechado"
    assert disjuntor.esta_aberto() is False

    # Estado antes da atuação automática
    assert disjuntor.status == "fechado"

    # Atuação automática
    disjuntor.atuar(True)
    assert disjuntor.status == "aberto"
    assert disjuntor.esta_aberto() is True


def test_protecao_eletrica_base_atuar():
    """
    Testa se o método atuar da classe base ProtecaoEletrica levanta NotImplementedError
    por meio de uma subclasse concreta que o chama diretamente.
    """

    class DummyProtecao(ProtecaoEletrica):
        def atuar(self, corrente):
            return super().atuar(corrente)

    dummy = DummyProtecao(nome="DUMMY", barra_origem=1)

    with pytest.raises(NotImplementedError):
        dummy.atuar(100.0)
