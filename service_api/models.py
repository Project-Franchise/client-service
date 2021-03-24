from sqlalchemy import Column, BIGINT, VARCHAR, Float, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from service_api import Base


class Realty(Base):

    __tablename__ = 'realty'

    id = Column(BIGINT, primary_key=True)
    location_id = Column(BIGINT, ForeignKey('location.id'), nullable=False)
    floor = Column(BIGINT, nullable=False)
    floors_number = Column(BIGINT, nullable=False)
    square = Column(BIGINT, nullable=False)
    rental_price = Column(Float)
    sale_price = Column(Float)
    building_state = Column(VARCHAR(255), nullable=False)
    published_at = Column(TIMESTAMP, nullable=False)
    original_id = Column(BIGINT, nullable=False)
    original_url = Column(VARCHAR(255), nullable=False)
    realty_type_id = Column(BIGINT, ForeignKey('realty_type.id'),
                            nullable=False)
    operation_type_id = Column(BIGINT, ForeignKey('operation_type.id'),
                               nullable=False)


class OperationType(Base):

    __tablename__ = 'operation_type'

    id = Column(BIGINT, primary_key=True)
    original_id = Column(BIGINT, nullable=False)
    name = Column(VARCHAR(255), nullable=False)
    realty = relationship('Realty', backref='operation_type', lazy=True)


class RealtyType(Base):

    __tablename__ = 'realty_type'

    id = Column(BIGINT, primary_key=True)
    original_id = Column(BIGINT, nullable=False)
    name = Column(VARCHAR(255), nullable=False)
    realty = relationship('Realty', backref='realty_type', lazy=True)


class Location(Base):

    __tablename__ = 'location'

    id = Column(BIGINT, primary_key=True)
    city_id = Column(BIGINT, ForeignKey('city.id'), nullable=False)
    street_name = Column(VARCHAR(255), nullable=False)
    building_number = Column(BIGINT, nullable=False)
    realty = relationship('Realty', backref='location', lazy=True)


class City(Base):

    __tablename__ = 'city'

    id = Column(BIGINT, primary_key=True)
    name = Column(VARCHAR(128), nullable=False)
    state_id = Column(BIGINT, ForeignKey('state.id'), nullable=False)
    original_id = Column(BIGINT, nullable=False)
    location = relationship('Location', backref='city', lazy=True)


class State(Base):

    __tablename__ = 'state'

    id = Column(BIGINT, primary_key=True)
    name = Column(VARCHAR(128), nullable=False)
    original_id = Column(BIGINT, nullable=False)
    city = relationship('City', backref='state', lazy=True)
