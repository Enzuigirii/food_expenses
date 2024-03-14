from __future__ import annotations

from typing import Optional
from typing import Sequence
from uuid import UUID

from sqlalchemy import delete
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from database.model import Products
from database.model import Shipments


class ShipmentsDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_shipment(
        self,
        shipment_num: str,
        shipment_status: str,
        shipment_date: str,
        shipping_address: str,
        shipping_cost: float,
        bonuses: int,
        assembly_and_delivery: int,
        discount: float,
    ) -> Shipments:
        new_shipment = Shipments(
            shipment_num=shipment_num,
            shipment_status=shipment_status,
            shipment_date=shipment_date,
            shipping_address=shipping_address,
            shipping_cost=shipping_cost,
            bonuses=bonuses,
            assembly_and_delivery=assembly_and_delivery,
            discount=discount
        )
        self.db_session.add(new_shipment)
        await self.db_session.flush()
        return new_shipment

    async def get_shipment_by_num(self, shipment_num: str) -> Optional[Shipments]:
        query = (
            select(Shipments)
            .where(Shipments.shipment_num == shipment_num)
        )
        result = await self.db_session.execute(query)
        shipmnet_row = result.fetchone()
        if shipmnet_row is not None:
            return shipmnet_row[0]
        return

    async def update_shipment_by_num(self, shipment_num: str, **kwargs) -> Optional[UUID]:
        query = (
            update(Shipments)
            .where(Shipments.shipment_num == shipment_num)
            .values(kwargs)
            .returning(Shipments.shipment_num)
        )
        result = await self.db_session.execute(query)
        updated_shipment_row = result.fetchone()
        if updated_shipment_row is not None:
            return updated_shipment_row[0]
        return

    async def delete_shipment_by_num(self, shipment_num: str) -> Optional[UUID]:
        query = (
            delete(Shipments)
            .where(Shipments.shipment_num == shipment_num)
            .returning(Shipments.shipment_num)
        )
        result = await self.db_session.execute(query)
        deleted_shipment_rows = result.fetchone()
        if deleted_shipment_rows is not None:
            return deleted_shipment_rows[0]
        return

    async def create_product(
        self,
        product_name: str,
        quantity: str,
        purchase_price: float,
        purchase_status: str,
        shipment_num: str
    ) -> Products:
        new_product = Products(
            product_name=product_name,
            quantity=quantity,
            purchase_price=purchase_price,
            purchase_status=purchase_status,
            shipment_num=shipment_num
        )
        self.db_session.add(new_product)
        await self.db_session.flush()
        return new_product

    async def get_products_by_shipment_num(self, shipment_num: str) -> Optional[Sequence]:
        query = (
            select(Products)
            .where(Products.shipment_num == shipment_num)
        )
        result = await self.db_session.scalars(query)
        product_rows = result.all()
        if product_rows is not None:
            return product_rows
        return

    async def update_product(self, product_id: UUID, **kwargs) -> Optional[UUID]:
        query = (
            update(Products)
            .where(Products.id == product_id)
            .values(kwargs)
            .returning(Products.id)
        )
        result = await self.db_session.execute(query)
        updated_product_row = result.fetchone()
        if updated_product_row is not None:
            return updated_product_row[0]
        return

    async def delete_products_by_shipment_num(self, shipment_num: str) -> Optional[Sequence]:
        query = (
            delete(Products)
            .where(Products.shipment_num == shipment_num)
            .returning(Products.id, Products.shipment_num)
        )
        result = await self.db_session.scalars(query)
        deleted_product_rows = result.all()
        if deleted_product_rows is not None:
            return deleted_product_rows
        return

    async def get_spending_report(self, date_from: str, date_to: str) -> dict:
        query = (
            select(
                func.count(Shipments.shipment_num),
                func.sum(Shipments.shipping_cost),
                func.sum(Shipments.shipping_cost) + func.sum(Shipments.bonuses)
            )
            .where(Shipments.shipment_date.between(date_from, date_to))
            .where(Shipments.shipment_status == 'Заказ доставлен')
        )
        result = await self.db_session.execute(query)
        report_row = result.fetchone()
        if report_row is not None:
            return {
                'report': (
                    f'Количество заказов: {report_row[0]}. '
                    f'На сумму {round(report_row[1], 2)} ₽, '
                    f'{round(report_row[2], 2)} ₽ с учётом трат бонусов.'
                )
            }
        return {'report': 'Ошибка в формировании отчёта.'}
