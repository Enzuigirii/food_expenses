import sys
import json
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_async_session
from api.actions import ShipmentRepository, ProductRepository
from api.schemas import CreateShipment, CreateProduct 
from settings import save_path_temp_files, temp_json_shipments

import asyncio
    
        
async def get_data_from_json(db_session: AsyncSession = get_async_session):
    
    with open(f"{save_path_temp_files}/{temp_json_shipments}.json", "r") as data:
        shipments = json.load(data)
        
        for shipment, shipment_data in shipments.items():    
            session = await anext(db_session())             
            await ShipmentRepository._create_new_shipment(
                CreateShipment(
                    shipment_num = shipment,
                    shipment_status = shipment_data.get("shipment_status"),
                    shipment_date = shipment_data.get("shipment_date"),
                    shipping_address = shipment_data.get("shipping_address"),
                    shipping_cost = shipment_data.get("shipping_cost"),
                    bonuses = shipment_data.get("bonuses"),
                    assembly_and_delivery = shipment_data.get("assembly_and_delivery"),
                    discount = shipment_data.get("discount"),
                ),
                session
            )
            
            products = shipment_data.get("products")
            
            for product, product_data in products.items():
                await ProductRepository._create_new_product(
                    CreateProduct(
                        product_name=product_data.get("product_name"),
                        quantity=product_data.get("quantity"),
                        purchase_price=product_data.get("purchase_price"),
                        purchase_status=product_data.get("purchase_status"),
                        shipment_num=shipment
                    ),
                    session
                )
                
            await session.close()

            
def main():
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(get_data_from_json())
    finally:
        loop.close()


if __name__ == '__main__':
    main()