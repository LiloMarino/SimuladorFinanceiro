from collections.abc import Callable


class LazyDict[K, V](
    dict[K, V],
):
    """
    Dicionário que carrega valores sob demanda usando um loader.

    Responsável por:
    - Carregar valores automaticamente quando uma chave é acessada pela primeira vez
    - Cachear valores carregados para acesso subsequente rápido
    - Implementar padrão lazy loading via método __missing__
    """

    def __init__(self, loader: Callable[[K], V]):
        super().__init__()
        self._loader = loader

    def __missing__(self, key: K) -> V:
        value = self._loader(key)
        self[key] = value
        return value
