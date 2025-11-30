from warnings import deprecated

from backend.core.decorators.transactional_method import transactional_method


@deprecated(
    "Use transactional_method for each method instead",
)
def transactional_class(cls):
    for name in dir(cls):
        if name.startswith("_"):
            continue

        attr = getattr(cls, name)

        # Só decora métodos de instância públicos
        if callable(attr):
            decorated = transactional_method(attr)
            setattr(cls, name, decorated)

    return cls
