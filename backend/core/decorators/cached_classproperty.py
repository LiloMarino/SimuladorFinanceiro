from collections.abc import Callable


class cached_classproperty[T]:  # noqa: N801
    def __init__(self, func: Callable[..., T]):
        self.func = func
        self.attr_name = f"__cached_{func.__name__}"

    def __get__(self, instance, owner) -> T:
        # se não tiver no cache da classe → cria
        if not hasattr(owner, self.attr_name):
            setattr(owner, self.attr_name, self.func(owner))
        # devolve a instância já criada
        return getattr(owner, self.attr_name)
