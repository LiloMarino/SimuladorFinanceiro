from backend.features.strategy.base_strategy import BaseStrategy


class ManualStrategy(BaseStrategy):
    """
    Estratégia manual que não executa ações automáticas.

    Responsável por:
    - Permitir controle total do player sem interferência automática
    - Servir como placeholder para simulações puramente manuais
    """

    def next(self):
        pass
