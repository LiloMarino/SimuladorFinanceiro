from typing import Callable, Generic, TypeVar

T = TypeVar("T")


class staticproperty(Generic[T]):
    def __init__(self, func: Callable[[], T]):
        self.func = func

    def __get__(self, instance, owner) -> T:
        return self.func()
