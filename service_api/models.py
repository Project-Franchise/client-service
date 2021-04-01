from sqlalchemy import (BIGINT, TIMESTAMP, VARCHAR, Column, Float, ForeignKey,
                        UniqueConstraint)
from sqlalchemy.orm import relationship

from service_api import Base


class RealtyDetails(Base):

    __tablename__ = "realty_details"

    id = Column(BIGINT, primary_key=True)
    realty = relationship("Realty", uselist=False, backref="realty_details")
    floor = Column(BIGINT, nullable=False)
    floors_number = Column(BIGINT, nullable=False)
    square = Column(BIGINT, nullable=False)
    price = Column(Float, nullable=False)
    published_at = Column(TIMESTAMP, nullable=False)
    original_id = Column(BIGINT, nullable=False, unique=True)
    original_url = Column(VARCHAR(255), nullable=False, unique=True)


class OperationType(Base):

    __tablename__ = "operation_type"

    id = Column(BIGINT, primary_key=True)
    original_id = Column(BIGINT, nullable=False, unique=True)
    name = Column(VARCHAR(255), nullable=False)
    realty = relationship("Realty", backref="operation_type", lazy=True)


class RealtyType(Base):

    __tablename__ = "realty_type"

    id = Column(BIGINT, primary_key=True)
    original_id = Column(BIGINT, nullable=False, unique=True)
    name = Column(VARCHAR(255), nullable=False)
    realty = relationship("Realty", backref="realty_type", lazy=True)


class Realty(Base):

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

    __tablename__ = "city"

    id = Column(BIGINT, primary_key=True)
    name = Column(VARCHAR(128), nullable=False)
    state_id = Column(BIGINT, ForeignKey(
        "state.id", ondelete="CASCADE"), nullable=False)
    original_id = Column(BIGINT, nullable=False, unique=True)
    realty = relationship("Realty", backref="city", lazy=True)


class State(Base):

    __tablename__ = "state"

    id = Column(BIGINT, primary_key=True)
    name = Column(VARCHAR(128), nullable=False)
    original_id = Column(BIGINT, nullable=False, unique=True)
    city = relationship("City", backref="state", lazy=True)
    realty = relationship("Realty", backref="state", lazy=True)
