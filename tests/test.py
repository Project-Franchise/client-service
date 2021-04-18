"""
Testing module
"""

from sqlalchemy.orm import Session
from service_api.models import State


def test_state_creation(reset_db: Session):
    """
    Adding state to db and checking if name is inserted right
    """
    data = {
        "name": "TestStateName",
        "original_id": 3,
    }
    state = State(**data)

    reset_db.add(state)
    reset_db.commit()

    state = reset_db.query(State).first()

    assert state.name == data["name"]
