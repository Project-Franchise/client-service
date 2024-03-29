"""
Models for service_api
"""
from datetime import datetime
from sqlalchemy import (BIGINT, TIMESTAMP, VARCHAR, Column, Float, ForeignKey, PrimaryKeyConstraint, UniqueConstraint)
from sqlalchemy.orm import relationship

from service_api import Base
from .constants import VERSION_DEFAULT_TIMESTAMP


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
    :param: original_url str
    """

    __tablename__ = "realty_details"

    id = Column(BIGINT, primary_key=True)
    realty = relationship("Realty", uselist=False, backref="realty_details", cascade="all,delete")
    floor = Column(BIGINT, nullable=True)
    floors_number = Column(BIGINT, nullable=True)
    square = Column(Float, nullable=True)
    price = Column(Float, nullable=False)
    published_at = Column(TIMESTAMP, nullable=False)
    original_url = Column(VARCHAR(255), nullable=False)
    version = Column(TIMESTAMP, nullable=True, default=VERSION_DEFAULT_TIMESTAMP)
    original_id = Column(BIGINT, nullable=True)

    __table_args__ = (
        UniqueConstraint(original_url, version),
    )


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
    city_id = Column(BIGINT, ForeignKey("city.id", ondelete="SET NULL"), nullable=True, unique=False)
    state_id = Column(BIGINT, ForeignKey("state.id", ondelete="CASCADE"), nullable=False, unique=False)
    realty_details_id = Column(BIGINT, ForeignKey(
        "realty_details.id", ondelete="CASCADE"), nullable=False, unique=False)
    realty_type_id = Column(BIGINT, ForeignKey("realty_type.id", ondelete="CASCADE"), nullable=False, unique=False)
    operation_type_id = Column(BIGINT, ForeignKey("operation_type.id",
                                                  ondelete="SET NULL"), nullable=True, unique=False)
    version = Column(TIMESTAMP, nullable=True, default=VERSION_DEFAULT_TIMESTAMP)
    service_id = Column(BIGINT, ForeignKey("service.id", ondelete="CASCADE"), nullable=False, unique=False)

    __table_args__ = (
        UniqueConstraint(city_id, state_id, realty_details_id, service_id,
                         realty_type_id, operation_type_id),
    )


class Service(Base):
    """
    Service model
    :param: id int
    :param: name str
    """

    __tablename__ = "service"

    id = Column(BIGINT, primary_key=True)
    name = Column(VARCHAR(128), nullable=False)
    city_to_service = relationship("CityXRefService", backref="service", lazy=True)
    state_to_service = relationship("StateXRefService", backref="service", lazy=True)
    operation_type_to_service = relationship("OperationTypeXRefService", backref="service", lazy=True)
    realty_type_to_service = relationship("RealtyTypeXRefService", backref="service", lazy=True)
    category_to_service = relationship("CategoryXRefService", backref="service", lazy=True)
    realty = relationship("Realty", backref="service", lazy=True)


class City(Base):
    """
    Realty type model
    :param: name str
    :param: state_id int
    """

    __tablename__ = "city"

    id = Column(BIGINT, primary_key=True)
    name = Column(VARCHAR(128), nullable=False)
    self_id = Column(BIGINT, nullable=False)
    version = Column(TIMESTAMP, nullable=True, default=VERSION_DEFAULT_TIMESTAMP)
    state_id = Column(BIGINT, ForeignKey("state.id", ondelete="CASCADE"), nullable=False)
    realty = relationship("Realty", backref="city", lazy=True)
    service_repr = relationship("CityXRefService", backref="entity", lazy=True)
    aliases = relationship("CityAlias", backref="city_type", lazy=True)

    __table_args__ = (
        UniqueConstraint("self_id", "version"),
    )


class CityXRefService(Base):
    """
    City to service model
    :param: city_id int
    :param: service_id int
    :param: original_id int
    """

    __tablename__ = "city_xref_service"

    entity_id = Column(BIGINT, ForeignKey("city.id", ondelete="CASCADE"), nullable=False)
    service_id = Column(BIGINT, ForeignKey("service.id", ondelete="CASCADE"), nullable=False)
    original_id = Column(VARCHAR(255), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("entity_id", "service_id"),
    )


class CityAlias(Base):
    """
    City alias model
    :param: city_id int
    :param: alias str
    """

    __tablename__ = "city_alias"

    entity_id = Column(BIGINT, ForeignKey("city.id", ondelete="CASCADE"), nullable=False)
    alias = Column(VARCHAR(255), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("entity_id", "alias"),
    )


class State(Base):
    """
    State type model
    :param: name str
    """

    __tablename__ = "state"

    id = Column(BIGINT, primary_key=True)
    name = Column(VARCHAR(128), nullable=False)
    city = relationship("City", backref="state", lazy=True)
    self_id = Column(BIGINT, nullable=False)
    version = Column(TIMESTAMP, nullable=True, default=VERSION_DEFAULT_TIMESTAMP)
    realty = relationship("Realty", backref="state", lazy=True)
    service_repr = relationship("StateXRefService", backref="entity", lazy=True)
    aliases = relationship("StateAlias", backref="state_type", lazy=True)

    __table_args__ = (UniqueConstraint("self_id", "version"),)


class StateXRefService(Base):
    """
    State to service model
    :param: state_id int
    :param: service_id int
    :param: original_id int
    """

    __tablename__ = "state_xref_service"

    entity_id = Column(BIGINT, ForeignKey("state.id", ondelete="CASCADE"), nullable=False)
    service_id = Column(BIGINT, ForeignKey("service.id", ondelete="CASCADE"), nullable=False)
    original_id = Column(VARCHAR(255), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("entity_id", "service_id"),
    )


class StateAlias(Base):
    """
    State alias model
    :param: state_id int
    :param: alias str
    """

    __tablename__ = "state_alias"

    entity_id = Column(BIGINT, ForeignKey("state.id", ondelete="CASCADE"), nullable=False)
    alias = Column(VARCHAR(255), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("entity_id", "alias"),
    )


class OperationType(Base):
    """
    Operation type model
    :param: name str
    :param: realty Realty
    """

    __tablename__ = "operation_type"

    id = Column(BIGINT, primary_key=True)
    name = Column(VARCHAR(255), nullable=False)
    self_id = Column(BIGINT, nullable=False)
    version = Column(TIMESTAMP, nullable=True, default=VERSION_DEFAULT_TIMESTAMP)
    realty = relationship("Realty", backref="operation_type", lazy=True)
    service_repr = relationship("OperationTypeXRefService", backref="entity", lazy=True)
    aliases = relationship("OperationTypeAlias", backref="operation_type", lazy=True)

    __table_args__ = (UniqueConstraint("self_id", "version"),)


class OperationTypeXRefService(Base):
    """
    Operation type to service model
    :param: operation_type_id int
    :param: service_id int
    :param: original_id int
    """

    __tablename__ = "operation_type_xref_service"

    entity_id = Column(BIGINT, ForeignKey("operation_type.id", ondelete="CASCADE"), nullable=False)
    service_id = Column(BIGINT, ForeignKey("service.id", ondelete="CASCADE"), nullable=False)
    original_id = Column(VARCHAR(255), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("entity_id", "service_id"),
    )


class OperationTypeAlias(Base):
    """
    Operation type alias model
    :param: operation_type int
    :param: alias str
    """

    __tablename__ = "operation_type_alias"

    entity_id = Column(BIGINT, ForeignKey("operation_type.id", ondelete="CASCADE"), nullable=False)
    alias = Column(VARCHAR(255), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("entity_id", "alias"),
    )


class RealtyType(Base):
    """
    Realty type model
    :param: name str
    :param: realty Realty
    """

    __tablename__ = "realty_type"

    id = Column(BIGINT, primary_key=True)
    name = Column(VARCHAR(255), nullable=False)
    category_id = Column(BIGINT, ForeignKey("category.id", ondelete="CASCADE"), nullable=False)
    self_id = Column(BIGINT, nullable=False)
    version = Column(TIMESTAMP, nullable=True, default=VERSION_DEFAULT_TIMESTAMP)
    realty = relationship("Realty", backref="realty_type", lazy=True)
    service_repr = relationship("RealtyTypeXRefService", backref="entity", lazy=True)
    aliases = relationship("RealtyTypeAlias", backref="realty_type", lazy=True)

    __table_args__ = (UniqueConstraint("self_id", "version"),)


class RealtyTypeXRefService(Base):
    """
    Realty type to service model
    :param: realty_type_id int
    :param: service_id int
    :param: original_id int
    """

    __tablename__ = "realty_type_xref_service"

    entity_id = Column(BIGINT, ForeignKey("realty_type.id", ondelete="CASCADE"), nullable=False)
    service_id = Column(BIGINT, ForeignKey("service.id", ondelete="CASCADE"), nullable=False)
    original_id = Column(VARCHAR(255), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("entity_id", "service_id"),
    )


class RealtyTypeAlias(Base):
    """
    Realty type alias model
    :param: realty_type int
    :param: alias str
    """

    __tablename__ = "realty_type_alias"

    entity_id = Column(BIGINT, ForeignKey("realty_type.id", ondelete="CASCADE"), nullable=False)
    alias = Column(VARCHAR(255), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("entity_id", "alias"),
    )


class Category(Base):
    """
    Category model
    :param: name str
    """

    __tablename__ = "category"

    id = Column(BIGINT, primary_key=True)
    name = Column(VARCHAR(255), nullable=False)
    self_id = Column(BIGINT, nullable=False)
    version = Column(TIMESTAMP, nullable=True, default=VERSION_DEFAULT_TIMESTAMP)
    service_repr = relationship("CategoryXRefService", backref="entity", lazy=True)
    aliases = relationship("CategoryAlias", backref="realty_type", lazy=True)

    __table_args__ = (UniqueConstraint("self_id", "version"),)


class CategoryXRefService(Base):
    """
    Category to service model
    :param: category_id int
    :param: service_id int
    :param: original_id int
    """

    __tablename__ = "category_xref_service"

    entity_id = Column(BIGINT, ForeignKey("category.id", ondelete="CASCADE"), nullable=False)
    service_id = Column(BIGINT, ForeignKey("service.id", ondelete="CASCADE"), nullable=False)
    original_id = Column(VARCHAR(255), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("entity_id", "service_id"),
    )


class CategoryAlias(Base):
    """
    Category alias model
    :param: category int
    :param: alias str
    """

    __tablename__ = "category_alias"

    entity_id = Column(BIGINT, ForeignKey("category.id", ondelete="CASCADE"), nullable=False)
    alias = Column(VARCHAR(255), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("entity_id", "alias"),
    )


class AdditionalFilters:
    """
    Class with all additional attributes for filters
    """
    page = None
    page_ads_number = None


class RequestsHistory(Base):
    """
    Requests history model
    :param: request_text str
    :param: request_timestamp datetime
    """

    __tablename__ = "requests_history"

    id = Column(BIGINT, primary_key=True)
    url = Column(VARCHAR(4096), nullable=False)
    hashed_token = Column(VARCHAR(200), nullable=False)
    request_timestamp = Column(TIMESTAMP, nullable=False, default=datetime.now())
