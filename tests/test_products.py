from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_products(client: TestClient) -> None:
    response = client.get("/products")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 6
    assert body["page"] == 1
    assert body["page_size"] == 20
    assert body["items"][0]["name"] == "Zenbook 14 OLED"


def test_search_products_by_query(client: TestClient) -> None:
    response = client.get("/products", params={"q": "gaming"})

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": 2,
                "name": "ROG Zephyrus G14",
                "category": "Gaming Laptop",
                "price": 62900.0,
            },
            {
                "id": 4,
                "name": "TUF Gaming A15",
                "category": "Gaming Laptop",
                "price": 38900.0,
            },
        ],
        "total": 2,
        "page": 1,
        "page_size": 20,
    }


def test_search_products_supports_sort_and_pagination(client: TestClient) -> None:
    response = client.get(
        "/products",
        params={"q": "laptop", "sort": "price", "order": "desc", "page": 2, "page_size": 2},
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": 1,
                "name": "Zenbook 14 OLED",
                "category": "Laptop",
                "price": 42900.0,
            },
            {
                "id": 4,
                "name": "TUF Gaming A15",
                "category": "Gaming Laptop",
                "price": 38900.0,
            },
        ],
        "total": 4,
        "page": 2,
        "page_size": 2,
    }


def test_list_products_rejects_unsupported_sort_field(client: TestClient) -> None:
    response = client.get("/products", params={"sort": "category"})

    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "literal_error",
                "loc": ["query", "sort"],
                "msg": "Input should be 'name' or 'price'",
                "input": "category",
                "ctx": {"expected": "'name' or 'price'"},
            }
        ]
    }


def test_list_products_rejects_invalid_order(client: TestClient) -> None:
    response = client.get("/products", params={"sort": "price", "order": "up"})

    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "literal_error",
                "loc": ["query", "order"],
                "msg": "Input should be 'asc' or 'desc'",
                "input": "up",
                "ctx": {"expected": "'asc' or 'desc'"},
            }
        ]
    }


def test_get_product(client: TestClient) -> None:
    response = client.get("/products/2")

    assert response.status_code == 200
    assert response.json()["name"] == "ROG Zephyrus G14"


def test_get_missing_product(client: TestClient) -> None:
    response = client.get("/products/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}
