"""
Models for service_api
"""
from sqlalchemy import (BIGINT, TIMESTAMP, VARCHAR, Column, Float, ForeignKey,
                        UniqueConstraint)
from sqlalchemy.orm import relationship

from service_api import Base


class RealtyDetails(Base):
    """
    Realty details model
    :param: realty Realty
    :param: floor int nullable
    :param: floors_number int nullable
    :param: square int nullable
    :param: price float
    :param: published_at datetime
    :param: floors_number int nullable
    :param: original_id int
    :param: original_url str
    """

    __tablename__ = "realty_details"

    id = Column(BIGINT, primary_key=True)
    realty = relationship("Realty", uselist=False, backref="realty_details", cascade="all,delete")
    floor = Column(BIGINT, nullable=True)
    floors_number = Column(BIGINT, nullable=True)
    square = Column(BIGINT, nullable=True)
    price = Column(Float, nullable=False)
    published_at = Column(TIMESTAMP, nullable=False)
    original_id = Column(BIGINT, nullable=False, unique=True)
    original_url = Column(VARCHAR(255), nullable=False, unique=True)


class OperationType(Base):
    """
    Operation type model
    :param: name str
    :param: realty Realty
    :param: original_id int
    """

    __tablename__ = "operation_type"

    id = Column(BIGINT, primary_key=True)
    original_id = Column(BIGINT, nullable=False, unique=True)
    name = Column(VARCHAR(255), nullable=False)
    realty = relationship("Realty", backref="operation_type", lazy=True)


class RealtyType(Base):
    """
    Realty type model
    :param: name str
    :param: realty Realty
    :param: original_id int
    """

    __tablename__ = "realty_type"

    id = Column(BIGINT, primary_key=True)
    original_id = Column(BIGINT, nullable=False, unique=True)
    name = Column(VARCHAR(255), nullable=False)
    realty = relationship("Realty", backref="realty_type", lazy=True)


class Realty(Base):
    """
    Realty model
    :param: city_id int
    :param: state_id int
    :param: realty_details_id int
    :param: realty_type_id int
    :param: operation_type_id int
    """

    __tablename__ = "realty"

    id = Column(BIGINT, primary_key=True)
    city_id = Column(BIGINT, ForeignKey("city.id", ondelete="SET NULL"), nullable=True)
    state_id = Column(BIGINT, ForeignKey("state.id", ondelete="CASCADE"), nullable=False)
    realty_details_id = Column(BIGINT, ForeignKey("realty_details.id", ondelete="CASCADE"), nullable=False, unique=True)
    realty_type_id = Column(BIGINT, ForeignKey("realty_type.id", ondelete="CASCADE"), nullable=False)
    operation_type_id = Column(BIGINT, ForeignKey("operation_type.id", ondelete="SET NULL"), nullable=True)

    __table_args__ = (
        UniqueConstraint(city_id, state_id, realty_details_id,
                         realty_type_id, operation_type_id),
    )


class City(Base):
    """
    Realty type model
    :param: name str
    :param: state_id int
    :param: original_id int
    """

    __tablename__ = "city"

    id = Column(BIGINT, primary_key=True)
    name = Column(VARCHAR(128), nullable=False)
    state_id = Column(BIGINT, ForeignKey(
        "state.id", ondelete="CASCADE"), nullable=False)
    original_id = Column(BIGINT, nullable=False, unique=True)
    realty = relationship("Realty", backref="city", lazy=True)


class State(Base):
    """
    Realty type model
    :param: name str
    :param: original_id int
    """

    __tablename__ = "state"

    id = Column(BIGINT, primary_key=True)
    name = Column(VARCHAR(128), nullable=False)
    original_id = Column(BIGINT, nullable=False, unique=True)
    city = relationship("City", backref="state", lazy=True)
    realty = relationship("Realty", backref="state", lazy=True)


class RequestsHistory(Base):
    """
    Requests history model
    :param: request_text str
    :param: request_timestamp datetime
    """

    __tablename__ = "requests_history"

    id = Column(BIGINT, primary_key=True)
    token_used = Column(VARCHAR(200), nullable=False)
    request_timestamp = Column(TIMESTAMP, nullable=False)