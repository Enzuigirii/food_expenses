
from sqlalchemy import ForeignKey
from sqlalchemy.types import DateTime, String, Integer, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import VARCHAR, UUID

import uuid
import datetime
from typing import Optional


class Base(DeclarativeBase):
    __abstract__ = True
    
    type_annotation_map = {
        int: Integer(),
        float: Float(),
        datetime.datetime: DateTime(timezone=True),
        str: String().with_variant(VARCHAR, "postgresql"),
        uuid.UUID: UUID(as_uuid=True)
    }

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
        )
    create_date: Mapped[datetime.datetime] = mapped_column(
        nullable=False,
        server_default=func.now()
        )
    last_updated: Mapped[datetime.datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
        server_onupdate=func.now()
        )
    

class Shipments(Base):
    __tablename__ = "shipments"

    shipment_num: Mapped[str] = mapped_column(unique=True, nullable=False)
    shipment_status: Mapped[Optional[str]]
    shipment_date: Mapped[Optional[str]]
    shipping_address: Mapped[Optional[str]]
    shipping_cost: Mapped[float] = mapped_column(nullable=False)
    bonuses: Mapped[Optional[int]]
    assembly_and_delivery: Mapped[Optional[int]]
    discount: Mapped[Optional[float]]
    products: Mapped["Products"] = relationship(back_populates="shipment")

class Products(Base):
    __tablename__ = "products"

    product_name: Mapped[Optional[str]]
    quantity: Mapped[Optional[str]]
    purchase_price: Mapped[Optional[float]]
    purchase_status: Mapped[Optional[str]]
    shipment_num: Mapped[str] = mapped_column(ForeignKey("shipments.shipment_num"))
    shipment: Mapped["Shipments"] = relationship(back_populates="products")
