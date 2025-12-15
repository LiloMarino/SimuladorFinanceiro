from collections.abc import Callable


class LazyDict[K, V](
    dict[K, V],
):
    """
    Dict que carrega valores sob demanda.

    loader: função(key: K) -> V
    """

    def __init__(self, loader: Callable[[K], V]):
        super().__init__()
        self._loader = loader

    def __missing__(self, key: K) -> V:
        value = self._loader(key)
        self[key] = value
        return value
