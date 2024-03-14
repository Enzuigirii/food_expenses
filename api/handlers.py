from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi import Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.actions import ShipmentRepository, ProductRepository, ReportRepository
from api.schemas import (
    ShowProduct, ShowShipment, CreateProduct, CreateShipment,
    UpdateShipmentRequest, UpdatedShipmentResponse, DeletedShipmentsResponse,
    UpdateProductRequest, UpdatedProductResponse, DeletedProductsResponse,
    ReportRequest, ReportResponse
)
from database.session import get_async_session


shipment_router = APIRouter()
product_router = APIRouter()
report_router = APIRouter()


@shipment_router.get("/", response_model=ShowShipment)
async def get_shipment(
    shipment_num: str, db: AsyncSession = Depends(get_async_session)
) -> ShowShipment:
    shipment = await ShipmentRepository._get_shipment_by_num(
        shipment_num=shipment_num, 
        session=db
    )
    return shipment


@shipment_router.post("/", response_model=ShowShipment)
async def create_shipment(
    body: CreateShipment, db: AsyncSession = Depends(get_async_session)
) -> ShowShipment:
    try:
        return await ShipmentRepository._create_new_shipment(body=body, session=db)
    except IntegrityError as err:
        raise HTTPException(status_code=503, detail=f"Ошибка базы данных: {err}")


@shipment_router.patch("/", response_model=UpdatedShipmentResponse)
async def update_shipment_by_num(
    shipment_num: str,
    body: UpdateShipmentRequest,
    db: AsyncSession = Depends(get_async_session)
):
    updated_params = body.model_dump(exclude_none=True)
    if not updated_params:
        raise HTTPException(
            status_code=422,
            detail="Укажите хотя бы один параметр для обновления"
        )
        
    shipment_for_update = await ShipmentRepository._get_shipment_by_num(
        shipment_num=shipment_num, 
        session=db
    )
    if shipment_for_update is None:
        raise HTTPException(
            status_code=404, detail=f"Номер доставки {shipment_num} отсутствует."
        )
        
    try:
        updated_shipment_num = await ShipmentRepository._update_shipment(
            updated_shipment_params=updated_params, 
            shipment_num=shipment_num, 
            session=db
        )
    except IntegrityError as err:
        raise HTTPException(status_code=503, detail=f"Ошибка базы данных: {err}")
    return UpdatedShipmentResponse(updated_shipment_num=updated_shipment_num)


@shipment_router.delete("/", response_model=DeletedShipmentsResponse)
async def delete_shipment(
    shipment_num: str, db: AsyncSession = Depends(get_async_session)
) -> DeletedShipmentsResponse:
    deleted_shipment_num = await ShipmentRepository._get_shipment_by_num(
        shipment_num=shipment_num, 
        session=db
    )
    if deleted_shipment_num is None:
        raise HTTPException(
            status_code=404, detail=f"Номер доставки {shipment_num} отсутствует."
        )
    try:
        deleted_shipment_num = await ShipmentRepository._delete_shipment_by_num(
            shipment_num=shipment_num, 
            session=db
        )
    except IntegrityError as err:
        raise HTTPException(
            status_code=503, 
            detail=f"Имеются внешние ссылки. Сначала удалите продукты. Ошибка: {err}"
        )   
    return DeletedShipmentsResponse(deleted_shipment_num=deleted_shipment_num)


@product_router.get("/", response_model=list[ShowProduct])
async def get_products(
    shipment_num: str, db: AsyncSession = Depends(get_async_session)
) -> list[ShowProduct]:
    products = await ProductRepository._get_products_by_shipment_num(
        shipment_num=shipment_num, 
        session=db
    )
    return products


@product_router.post("/", response_model=ShowProduct)
async def create_product(
    body: CreateProduct, db: AsyncSession = Depends(get_async_session)
) -> ShowProduct:
    try:
        return await ProductRepository._create_new_product(body=body, session=db)
    except IntegrityError as err:
        raise HTTPException(
            status_code=503, 
            detail=f"Сначала создайте информацию о доставке. Ошибка: {err}"
        )


@product_router.patch("/", response_model=UpdatedProductResponse)
async def update_product_by_id(
    product_id: UUID,
    body: UpdateProductRequest,
    db: AsyncSession = Depends(get_async_session)
) -> UpdatedProductResponse:
    updated_params = body.model_dump(exclude_none=True)
    if not updated_params:
        raise HTTPException(
            status_code=422,
            detail="Укажите хотя бы один параметр для обновления"
        )
    try:
        updated_product_id = await ProductRepository._update_product(
           updated_product_params=updated_params, 
           product_id=product_id,
           session=db
        )
    except IntegrityError as err:
        raise HTTPException(
            status_code=503, 
            detail=f"Проверьте существует ли указанная Вами доставка. Ошибка базы данных: {err}"
        )
    return UpdatedProductResponse(updated_product_id=updated_product_id)
    

@product_router.delete("/",  response_model=list[DeletedProductsResponse])
async def delete_products(
    shipment_num: str, db: AsyncSession = Depends(get_async_session)
) -> list[DeletedProductsResponse]:
    products_for_delete = await ProductRepository._get_products_by_shipment_num(
        shipment_num=shipment_num, 
        session=db
    )
    if products_for_delete is None:
        raise HTTPException(
            status_code=404, 
            detail=f"По номеру доставки {shipment_num} отсутствуют продукты"
        )
    deleted_products = await ProductRepository._delete_products_by_shipment_num(
        shipment_num=shipment_num, 
        session=db
    )
    return deleted_products

@report_router.get("/", response_model=ReportResponse)
async def get_spending_report(
    date_from: str, 
    date_to: str, 
    db: AsyncSession = Depends(get_async_session)
) -> ReportResponse:
    body = ReportRequest(date_from=date_from, date_to=date_to)
    report = await ReportRepository._get_spending_report(
        body=body,
        session=db
    )
    return report

