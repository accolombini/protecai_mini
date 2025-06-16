"""
ieee14.py

Módulo de carregamento e exportação do sistema IEEE 14 barras utilizando a biblioteca pandapower.
Desenvolvido com foco em boas práticas de programação, PEP 8 e docstrings padrão Google.
"""

import pandapower as pp
import pandapower.networks as pn


class IEEE14System:
    """Classe que representa o sistema IEEE 14 barras."""

    def __init__(self):
        """Inicializa o sistema carregando o modelo IEEE 14."""
        self.net = pn.case14()

    def export_to_json(self, path: str) -> None:
        """
        Exporta o sistema IEEE 14 barras para um arquivo JSON.

        Args:
            path (str): Caminho do arquivo de destino.
        """
        pp.to_json(self.net, path)

    def run_power_flow(self, calculate_voltage_angles: bool = True) -> None:
        """
        Executa a simulação de fluxo de carga (power flow).

        Args:
            calculate_voltage_angles (bool): Se True, calcula ângulos de tensão.
        """
        pp.runpp(self.net, calculate_voltage_angles=calculate_voltage_angles)

    def get_bus_voltages(self):
        """
        Retorna as tensões nas barras do sistema.

        Returns:
            list: Lista de tuplas com (bus index, voltage in pu).
        """
        return list(zip(self.net.bus.index.tolist(), self.net.res_bus.vm_pu.tolist()))

    def get_line_currents(self):
        """
        Retorna as correntes nas linhas.

        Returns:
            list: Lista de tuplas com (from_bus, to_bus, current in kA).
        """
        currents = self.net.res_line.i_ka.tolist()
        from_buses = self.net.line.from_bus.tolist()
        to_buses = self.net.line.to_bus.tolist()
        return list(zip(from_buses, to_buses, currents))
