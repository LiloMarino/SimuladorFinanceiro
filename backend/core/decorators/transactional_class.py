from backend.core.decorators.transactional_method import transactional_method


def transactional_class(cls):
    for attr_name, attr_value in cls.__dict__.items():
        # Só decora métodos públicos normais
        if callable(attr_value) and not attr_name.startswith("_"):
            setattr(cls, attr_name, transactional_method(attr_value))
    return cls
