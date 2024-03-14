from __future__ import annotations

import datetime
import re
import uuid
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel
from pydantic import validator


STRING_DATE_MATCH_PATTERN = re.compile(r'\d{4}-\d{2}-\d{2}')


class TunedModel(BaseModel):
    class Config:
        """tells pydantic to convert even non dict obj to json"""

        from_attributes = True


class ShowShipment(TunedModel):
    id: uuid.UUID
    create_date: datetime.datetime
    last_updated: datetime.datetime
    shipment_num: str
    shipment_status: Optional[str]
    shipment_date: Optional[str]
    shipping_address: Optional[str]
    shipping_cost: float
    bonuses: Optional[int]
    assembly_and_delivery: Optional[int]
    discount: Optional[float]


class CreateShipment(BaseModel):
    shipment_num: str
    shipment_status: Optional[str]
    shipment_date: Optional[str]
    shipping_address: Optional[str]
    shipping_cost: float
    bonuses: Optional[int]
    assembly_and_delivery: Optional[int]
    discount: Optional[float]


class UpdateShipmentRequest(BaseModel):
    shipment_status: Optional[str]
    shipment_date: Optional[str]
    shipping_address: Optional[str]
    shipping_cost: float
    bonuses: Optional[int]
    assembly_and_delivery: Optional[int]
    discount: Optional[float]


class UpdatedShipmentResponse(BaseModel):
    updated_shipment_num: str


class DeletedShipmentsResponse(BaseModel):
    deleted_shipment_num: str


class ShowProduct(TunedModel):
    id: uuid.UUID
    create_date: datetime.datetime
    last_updated: datetime.datetime
    product_name: Optional[str]
    quantity: Optional[str]
    purchase_price: Optional[float]
    purchase_status: Optional[str]
    shipment_num: str


class CreateProduct(BaseModel):
    product_name: Optional[str]
    quantity: Optional[str]
    purchase_price: Optional[float]
    purchase_status: Optional[str]
    shipment_num: str


class UpdateProductRequest(BaseModel):
    product_name: Optional[str]
    quantity: Optional[str]
    purchase_price: Optional[float]
    purchase_status: Optional[str]
    shipment_num: Optional[str]


class UpdatedProductResponse(BaseModel):
    updated_product_id: uuid.UUID


class DeletedProductsResponse(BaseModel):
    deleted_products_id: uuid.UUID


class ReportRequest(BaseModel):
    date_from: str
    date_to: str

    @validator('date_from')
    def validate_date_from(cls, value):
        if not STRING_DATE_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail='Дата должна быть в формате yyyy-mm-dd.'
            )
        return value

    @validator('date_to')
    def validate_date_to(cls, value):
        if not STRING_DATE_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail='Дата должна быть в формате yyyy-mm-dd.'
            )
        return value


class ReportResponse(TunedModel):
    report: str
