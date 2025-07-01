# Este script define a configuração lógica dos dispositivos de proteção
# para o modelo IEEE 14 Barras estendido, e deve ser armazenado em:
# simuladores/power_sim/config_protecao.py

from infra.protecao.protecao_eletrica import (
    Rele50, Rele51, Rele67, Rele87T, Disjuntor
)


def configurar_dispositivos_protecao():
    """
    Mapeia e instancia os dispositivos de proteção do sistema IEEE 14 Barras modificado.
    Cada dispositivo é representado por um objeto com parâmetros definidos conforme norma ANSI.

    Returns:
        dict: Dicionário com listas de relés e disjuntores
    """
    reles = []
    disjuntores = []

    # Relé diferencial de transformador (Barra 1)
    reles.append(Rele87T(nome="87T_B1", barra_origem=1, corrente_disparo=800.0,
                         corrente_secundario=780.0, transformador_id="TR_B1"))

    # Relé direcional (Barra 2)
    reles.append(Rele67(nome="67_B2", barra_origem=2, corrente_disparo=400.0,
                        direcao="ida", tempo_atuacao=0.2))

    # Relé temporizado de sobrecorrente (Barra 4)
    reles.append(Rele51(nome="51_B4", barra_origem=4, corrente_disparo=300.0,
                        tempo_atuacao=0.4))

    # Relé direcional de backup (Linha 6-13)
    reles.append(Rele67(nome="67_L6_13", barra_origem=6, corrente_disparo=250.0,
                        direcao="ida", tempo_atuacao=0.3))

    # Relé instantâneo de sobrecorrente (Barra 7)
    reles.append(Rele50(nome="50_B7", barra_origem=7, corrente_disparo=600.0))

    # Disjuntores acoplados aos relés
    for rele in reles:
        disjuntores.append(
            Disjuntor(nome=f"DJ_{rele.nome}", barra_origem=rele.barra_origem))

    return {
        "reles": reles,
        "disjuntores": disjuntores
    }


if __name__ == "__main__":
    protecao = configurar_dispositivos_protecao()
    print(
        f"Dispositivos de Proteção configurados: {len(protecao['reles'])} relés e {len(protecao['disjuntores'])} disjuntores.")
