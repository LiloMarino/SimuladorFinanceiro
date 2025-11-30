from functools import wraps

from backend.core.database import SessionLocal


def transactional_method(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        session = SessionLocal()
        try:
            result = func(self, session, *args, **kwargs)

            # Commit somente em alterações (UPDATE/INSERT/DELETE)
            if session.dirty or session.new or session.deleted:
                session.commit()

            return result

        except Exception:
            session.rollback()
            raise

        finally:
            session.close()

    return wrapper
