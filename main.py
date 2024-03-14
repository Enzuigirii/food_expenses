from fastapi import FastAPI, APIRouter
import uvicorn

from api.handlers import shipment_router, product_router, report_router


app = FastAPI(title="food-expenses")  # noqa: pylint=invalid-name

main_router = APIRouter()
main_router.include_router(shipment_router, prefix="/shipment", tags=["shipment"])
main_router.include_router(product_router, prefix="/product", tags=["product"])
main_router.include_router(report_router, prefix="/report", tags=["report"])

app.include_router(main_router)


if __name__ == '__main__':
    uvicorn.run("main:app", port=8000, host="0.0.0.0", reload=True)