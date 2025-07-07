from pathlib import Path
import pandapower as pp
import os
import time


class IEEE14System:
    """
    Classe responsável por carregar e disponibilizar o sistema IEEE 14 Barras
    com dispositivos de proteção modelados (relés, disjuntores, transformadores, etc).

    O arquivo JSON é carregado a partir do diretório "simuladores/power_sim/data",
    garantindo compatibilidade com a versão 2.14.1 do Pandapower.
    """

    def __init__(self):
        """
        Inicializa a instância carregando a topologia elétrica a partir de um arquivo JSON
        gerado previamente por `to_json()` do pandapower.
        Inclui verificação se o arquivo está disponível localmente ou em cache do iCloud.
        """
        path = Path(__file__).resolve().parent / \
            "data" / "ieee14_protecao.json"

        # Se o arquivo estiver em cache do iCloud (ainda não baixado), forçamos o download
        if not path.exists():
            icloud_stub = path.with_suffix(path.suffix + ".icloud")
            if icloud_stub.exists():
                print("⚠️ Arquivo está na nuvem. Solicitando download do iCloud...")
                os.system(f"brctl download '{path}'")
                for _ in range(10):  # Aguarda até 5 segundos (0.5 * 10)
                    if path.exists():
                        break
                    time.sleep(0.5)

        if not path.exists():
            raise FileNotFoundError(
                f"Arquivo JSON não encontrado ou não foi baixado: {path}")

        try:
            # Carrega o JSON customizado
            import json
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Extrai a rede PandaPower da string JSON
            self.net = pp.from_json_string(data["pandapower_net"])
        except Exception as e:
            raise ValueError(
                f"Erro ao carregar a rede a partir do JSON. Verifique se foi exportado corretamente\nDetalhes: {e}"
            )

    def get_network(self):
        """
        Retorna o objeto `net` do pandapower com todos os dados carregados.

        Returns:
            pandapowerNet: Rede elétrica completa com os dispositivos modelados.
        """
        return self.net
