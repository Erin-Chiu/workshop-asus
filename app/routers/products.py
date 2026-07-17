from typing import Annotated, Literal

from fastapi import APIRouter, HTTPException, Query, status

from app.models import Product, ProductPage
from app.repository import get_product, search_products

router = APIRouter(prefix="/products", tags=["products"])

SortField = Literal["name", "price", "category"]
SortOrder = Literal["asc", "desc"]


@router.get("", response_model=ProductPage)
def read_products(
    q: str | None = None,
    sort: SortField | None = None,
    order: SortOrder = "asc",
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=20)] = 20,
) -> ProductPage:
    products = search_products(q=q, sort=sort, order=order)
    total = len(products)
    start = (page - 1) * page_size
    items = products[start : start + page_size]
    return ProductPage(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{product_id}", response_model=Product)
def read_product(product_id: int) -> Product:
    product = get_product(product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return product
