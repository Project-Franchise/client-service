"""
Config module for pytest
"""
import pytest
from service_api import Base, engine, session


@pytest.fixture
def reset_db():
    """
    Main setup and teardown fixture that is reseting database
    """
    Base.metadata.create_all(engine)
    yield session
    session.close()
    Base.metadata.drop_all(engine)
