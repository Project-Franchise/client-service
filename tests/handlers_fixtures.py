"""
Fixture for pytest
"""
import pytest
from service_api import session_scope, Base, engine


@pytest.fixture(scope="function")
def set_database():
    """
    Create all tables in test db and drop after executing
    """
    Base.metadata.create_all(engine)
    yield
    with session_scope() as session:
        session.close()
        Base.metadata.drop_all(engine)
