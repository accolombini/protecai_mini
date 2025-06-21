# protecao_eletrica.py
'''
    Módulo de Proteção Elétrica
    Define classes para dispositivos de proteção elétrica como relés e disjuntores.
    Utiliza herança para criar uma hierarquia de dispositivos com métodos específicos de atuação.
    Utiliza a biblioteca `abc` para definir classes abstratas e métodos abstratos.
    Utiliza do módulo abc (Abstract Base Classes), que está disponível por padrão em todas as versões Python 3.x.  Fundamentais para definir contratos (interfaces abstratas) e garantir que subclasses implementem determinados métodos — exatamente o que precisamos para relés, disjuntores e futuros algoritmos de atuação.
'''
from abc import ABC, abstractmethod


class ProtecaoEletrica(ABC):
    """Classe base abstrata para dispositivos de proteção elétrica."""

    def __init__(self, nome: str, barra_origem: int, barra_destino: int = None,
                 corrente_disparo: float = None, tempo_atuacao: float = None):
        """
        Inicializa um dispositivo de proteção elétrica.

        Args:
            nome (str): Nome ou identificador do dispositivo.
            barra_origem (int): ID da barra de origem.
            barra_destino (int, optional): ID da barra de destino (se aplicável).
            corrente_disparo (float, optional): Corrente de disparo em A.
            tempo_atuacao (float, optional): Tempo de atuação em segundos.
        """
        self.nome = nome
        self.barra_origem = barra_origem
        self.barra_destino = barra_destino
        self.corrente_disparo = corrente_disparo
        self.tempo_atuacao = tempo_atuacao

    @abstractmethod
    def atuar(self, corrente):
        """Deve ser implementado por subclasses concretas"""
        raise NotImplementedError("Método abstrato deve ser implementado.")


class Rele51(ProtecaoEletrica):
    """Relé de sobrecorrente (ANSI 50/51)."""

    def atuar(self, corrente: float) -> bool:
        return corrente >= self.corrente_disparo


class Rele67(ProtecaoEletrica):
    """Relé de sobrecorrente direcional (ANSI 67)."""

    def __init__(self, direcao: str, **kwargs):
        super().__init__(**kwargs)
        self.direcao = direcao  # 'ida' ou 'volta'

    def atuar(self, corrente: float, direcao_fluxo: str) -> bool:
        return corrente >= self.corrente_disparo and direcao_fluxo == self.direcao


class Rele87T(ProtecaoEletrica):
    """Relé diferencial de transformador (ANSI 87T)."""

    def __init__(self, transformador_id: str, corrente_secundario: float, **kwargs):
        super().__init__(**kwargs)
        self.transformador_id = transformador_id
        self.corrente_secundario = corrente_secundario

    def atuar(self, corrente_primario: float) -> bool:
        delta_i = abs(corrente_primario - self.corrente_secundario)
        return delta_i >= self.corrente_disparo


class Rele27(ProtecaoEletrica):
    """Relé de subtensão (ANSI 27)."""

    def atuar(self, tensao: float) -> bool:
        return tensao <= self.corrente_disparo  # neste caso representa tensão limite


class Rele59(ProtecaoEletrica):
    """Relé de sobretensão (ANSI 59)."""

    def atuar(self, tensao: float) -> bool:
        return tensao >= self.corrente_disparo


class Disjuntor(ProtecaoEletrica):
    """Disjuntor com tempo de atuação."""

    def __init__(self, status: str = "fechado", **kwargs):
        super().__init__(**kwargs)
        self.status = status  # 'aberto' ou 'fechado'

    def abrir(self):
        self.status = "aberto"

    def fechar(self):
        self.status = "fechado"

    def esta_aberto(self) -> bool:
        return self.status == "aberto"

    def atuar(self, comando: bool) -> None:
        if comando:
            self.abrir()
