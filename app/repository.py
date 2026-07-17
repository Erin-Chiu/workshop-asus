from app.models import Product

PRODUCTS = [
    Product(id=1, name="Zenbook 14 OLED", category="Laptop", price=42900),
    Product(id=2, name="ROG Zephyrus G14", category="Gaming Laptop", price=62900),
    Product(id=3, name="ProArt P16", category="Creator Laptop", price=79900),
    Product(id=4, name="TUF Gaming A15", category="Gaming Laptop", price=38900),
    Product(id=5, name="ROG Ally X", category="Handheld", price=26900),
    Product(id=6, name="ProArt Display PA279CRV", category="Monitor", price=15900),
]


def list_products() -> list[Product]:
    return PRODUCTS.copy()


def get_product(product_id: int) -> Product | None:
    return next((product for product in PRODUCTS if product.id == product_id), None)


def search_products(
    q: str | None,
    sort: str | None,
    order: str,
) -> list[Product]:
    results = PRODUCTS.copy()
    if q is not None:
        needle = q.lower()
        results = [
            p for p in results if needle in p.name.lower() or needle in p.category.lower()
        ]
    if sort is not None:
        reverse = order == "desc"
        results = sorted(results, key=lambda p: getattr(p, sort), reverse=reverse)
    return results

