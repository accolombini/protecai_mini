"""
Módulo de definição do sistema IEEE 14 barras.
Gera a rede utilizando a API moderna do pandapower.
"""

from pathlib import Path
import pandapower as pp


class IEEE14System:
    """
    Classe para gerar e exportar o sistema IEEE 14 barras.
    """

    def __init__(self):
        """
        Inicializa o objeto com a rede IEEE 14 importada de JSON.

        Observação:
        Caso deseje construir a rede programaticamente,
        utilize o método interno `_create_ieee14()`.
        """
        path = Path(__file__).resolve().parent / "data" / "ieee14.json"
        self.net = pp.from_json(str(path))

        # Elimina warnings relacionados à ausência de tap_dependency_table
        self._inicializar_tap_config()

    def _inicializar_tap_config(self):
        """
        Inicializa a estrutura de TAP na rede para prevenir warnings deprecatórios.
        """
        if 'tap_dependency_table' not in self.net:
            self.net['tap_dependency_table'] = {}

        if 'trafo' in self.net and not self.net.trafo.empty:
            for tid in self.net.trafo.index:
                self.net.trafo.at[tid, 'tap_side'] = 'hv'
                self.net.trafo.at[tid, 'tap_step_percent'] = 0.0
                self.net.trafo.at[tid, 'tap_pos'] = 0
                self.net.trafo.at[tid, 'tap_neutral'] = 0
                self.net.trafo.at[tid, 'tap_min'] = 0
                self.net.trafo.at[tid, 'tap_max'] = 0

    def _create_ieee14(self):
        """
        Cria o sistema IEEE 14 com base em parâmetros simplificados.

        Returns:
            pp.pandapowerNet: Objeto da rede.
        """
        net = pp.create_empty_network()

        # Exemplo simplificado — substitua por dados reais
        b1 = pp.create_bus(net, vn_kv=132)
        b2 = pp.create_bus(net, vn_kv=132)
        pp.create_line_from_parameters(net, b1, b2, length_km=1.0,
                                       r_ohm_per_km=0.1, x_ohm_per_km=0.2,
                                       c_nf_per_km=10, max_i_ka=0.4)
        pp.create_ext_grid(net, bus=b1, vm_pu=1.02, name="Grid Connection")
        pp.create_load(net, bus=b2, p_mw=20, q_mvar=5, name="Load Bus 2")

        # Inserção preventiva de estrutura de TAP
        net['tap_dependency_table'] = {}

        return net

    def export(self, path: str):
        """
        Exporta a rede para um arquivo JSON.

        Args:
            path (str): Caminho completo do arquivo de destino.
        """
        pp.to_json(self.net, path)

    def get_network(self):
        """
        Retorna a rede pandapower carregada.

        Returns:
            pp.pandapowerNet: Objeto da rede.
        """
        return self.net
