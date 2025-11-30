from typing import Callable, Generic, TypeVar
from warnings import deprecated

T = TypeVar("T")


@deprecated("Use cached_classproperty instead")
class staticproperty(Generic[T]):
    """Deprecated, use cached_classproperty instead."""

    def __init__(self, func: Callable[[], T]):
        self.func = func

    def __get__(self, instance, owner) -> T:
        return self.func()
