import models
from contextlib import contextmanager

@contextmanager
def get_session():
    """Provide a transactional scope around a series of operations."""
    if models.Session is None:
        models.init_db()
    session = models.Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
