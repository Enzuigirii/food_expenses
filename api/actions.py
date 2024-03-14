from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import (ShowShipment, CreateShipment, 
                         ShowProduct, CreateProduct,
                         ReportRequest, ReportResponse,
                         DeletedProductsResponse)
from database.dal import ShipmentsDAL
from database.model import Shipments, Products


class ShipmentRepository:
    @classmethod
    async def _create_new_shipment(
        cls, body: CreateShipment, session: AsyncSession
    ) -> ShowShipment:
        async with session.begin():
            shipment_dal = ShipmentsDAL(session)
            shipment = await shipment_dal.create_shipment(
                shipment_num=body.shipment_num,
                shipment_status=body.shipment_status,
                shipment_date=body.shipment_date,
                shipping_address=body.shipping_address,
                shipping_cost=body.shipping_cost,
                bonuses=body.bonuses,
                assembly_and_delivery=body.assembly_and_delivery,
                discount=body.discount
            )
            return ShowShipment(
                id=shipment.id,
                create_date=shipment.create_date,
                last_updated=shipment.last_updated,
                shipment_num=shipment.shipment_num,
                shipment_status=shipment.shipment_status,
                shipment_date=shipment.shipment_date,
                shipping_address=shipment.shipping_address,
                shipping_cost=shipment.shipping_cost,
                bonuses=shipment.bonuses,
                assembly_and_delivery=shipment.assembly_and_delivery,
                discount=shipment.discount
            )

    @classmethod
    async def _get_shipment_by_num(
        cls, shipment_num: str, session: AsyncSession
    ) -> Optional[Shipments]:
        async with session.begin():
            shipment_dal = ShipmentsDAL(session)
            shipment = await shipment_dal.get_shipment_by_num(
                shipment_num=shipment_num,
            )
            if shipment is not None:
                return shipment
            return

    @classmethod
    async def _update_shipment(
        cls, updated_shipment_params: dict, shipment_num: str, session: AsyncSession
    ) -> Optional[UUID]:
        async with session.begin():
            shipment_dal = ShipmentsDAL(session)
            updated_shipment_num = await shipment_dal.update_shipment_by_num(
                shipment_num=shipment_num, **updated_shipment_params
            )
            return updated_shipment_num
        
    @classmethod    
    async def _delete_shipment_by_num(
        cls, shipment_num: str, session: AsyncSession
    ) -> Optional[Products]:
        async with session.begin():
            shipments_dal = ShipmentsDAL(session)
            deleted_shipment = await shipments_dal.delete_shipment_by_num(
                shipment_num=shipment_num
            )
            return deleted_shipment


class ProductRepository:
    @classmethod
    async def _create_new_product(
        cls, body: CreateProduct, session: AsyncSession
    ) -> ShowProduct:
        shipment_dal = ShipmentsDAL(session)
        product = await shipment_dal.create_product(
            product_name=body.product_name,
            quantity=body.quantity,
            purchase_price=body.purchase_price,
            purchase_status=body.purchase_status,
            shipment_num=body.shipment_num
        )   
        return ShowProduct(
            id=product.id,
            create_date=product.create_date,
            last_updated=product.last_updated,
            product_name=product.product_name,
            quantity=product.quantity,
            purchase_price=product.purchase_price,
            purchase_status=product.purchase_status,
            shipment_num=product.shipment_num
        )
        
    @classmethod    
    async def _get_products_by_shipment_num(
        cls, shipment_num: str, session: AsyncSession
    ) -> Optional[Sequence[ShowProduct]]:
        async with session.begin():
            shipments_dal = ShipmentsDAL(session)
            product_models = await shipments_dal.get_products_by_shipment_num(
                shipment_num=shipment_num
            )
            if product_models is not None:
                products = [ShowProduct.model_validate(product) for product in product_models]
                return products
            return 
            
    @classmethod                
    async def _update_product(
        cls, updated_product_params: dict, product_id: UUID, session: AsyncSession
    ) -> Optional[Products]:
        async with session.begin():
            shipment_dal = ShipmentsDAL(session)
            updated_product = await shipment_dal.update_product(
                product_id=product_id, **updated_product_params
            )
            return updated_product
        
    @classmethod    
    async def _delete_products_by_shipment_num(
        cls, shipment_num: str, session: AsyncSession
    ) -> Optional[Sequence[DeletedProductsResponse]]:
        async with session.begin():
            shipments_dal = ShipmentsDAL(session)
            deleted_products = await shipments_dal.delete_products_by_shipment_num(
                shipment_num=shipment_num
            )
            if deleted_products is not None:
                deleted_products = [{'deleted_products_id': id_} for id_ in deleted_products] 
                return deleted_products
            return 

    
class ReportRepository:
    @classmethod 
    async def _get_spending_report(
        cls, body: ReportRequest, session: AsyncSession
    ) -> ReportResponse:
        async with session.begin():
            shipments_dal = ShipmentsDAL(session)
            report = await shipments_dal.get_spending_report(
                date_from=body.date_from, 
                date_to=body.date_to
            )
            return report