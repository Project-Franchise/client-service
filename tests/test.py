"""
Testing module
"""

from service_api.models import State
from service_api import Session_factory, Base, engine

session = Session_factory()


def setup_function():
    """
    Create all table in DB
    """
    Base.metadata.create_all(engine)

def teardown_function():
    """
    Closes session if its open and drop database
    """
    session.close()
    Base.metadata.drop_all(engine)

def test_state_creation():
    """
    Adding state to db and checking if name is inserted right
    """
    data = {
        "name": "TestStateName",
        "self_id": 3,
    }
    state = State(**data)

    session.add(state)
    session.commit()

    state = session.query(State).first()

    assert state.name == data["name"]
