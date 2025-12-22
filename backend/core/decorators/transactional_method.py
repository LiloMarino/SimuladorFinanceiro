from collections.abc import Callable
from functools import wraps
from typing import Concatenate, ParamSpec, TypeVar

from sqlalchemy.orm import Session

from backend.core.database import SessionLocal

T = TypeVar("T")
P = ParamSpec("P")
R = TypeVar("R")


def transactional(
    func: Callable[Concatenate[T, Session, P], R],
) -> Callable[Concatenate[T, P], R]:
    @wraps(func)
    def wrapper(self: T, *args: P.args, **kwargs: P.kwargs) -> R:
        session = SessionLocal()
        try:
            result = func(self, session, *args, **kwargs)
            session.commit()
        except Exception:
            session.rollback()
            raise
        else:
            return result
        finally:
            session.close()

    return wrapper
