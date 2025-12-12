class LazyDict(dict):
    """
    Dict que carrega valores sob demanda.

    loader: função(key) -> value
    """

    def __init__(self, loader):
        super().__init__()
        self.loader = loader

    def __missing__(self, key):
        value = self.loader(key)
        self[key] = value
        return value
