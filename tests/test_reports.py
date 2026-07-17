import pytest
from fastapi.testclient import TestClient


def test_sales_report_returns_category_items_and_total(client: TestClient) -> None:
    response = client.get("/reports/sales", params={"category": "Laptop"})

    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "Laptop"
    assert len(body["items"]) == 1
    assert body["items"][0]["name"] == "Zenbook 14 OLED"
    assert body["total"] == pytest.approx(42900.0)


def test_sales_report_formula_applies_arithmetic(client: TestClient) -> None:
    response = client.get(
        "/reports/sales",
        params={"category": "Gaming Laptop", "formula": "total * 2"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == pytest.approx(62900.0 * 2)


def test_sales_report_sql_injection_returns_empty(client: TestClient) -> None:
    """SQL injection via category must not leak rows from other categories."""
    response = client.get(
        "/reports/sales",
        params={"category": "' OR '1'='1"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["total"] == 0


def test_sales_report_formula_code_injection_rejected(client: TestClient) -> None:
    """formula must not be able to execute arbitrary Python code."""
    response = client.get(
        "/reports/sales",
        params={"category": "Laptop", "formula": "__import__('os').system('id')"},
    )

    assert response.status_code == 422
    body = response.json()
    assert "detail" in body
    # Must not contain stack traces or implementation details
    assert "Traceback" not in body["detail"]


def test_sales_report_formula_builtin_injection_rejected(client: TestClient) -> None:
    """formula must reject expressions that reference builtins."""
    response = client.get(
        "/reports/sales",
        params={"category": "Laptop", "formula": "open('/etc/passwd').read()"},
    )

    assert response.status_code == 422


def test_sales_report_error_does_not_disclose_stack_trace(client: TestClient) -> None:
    """Error responses must not include stack traces or internal details."""
    response = client.get(
        "/reports/sales",
        params={"category": "Laptop", "formula": "1/0"},
    )

    assert response.status_code == 422
    body = response.json()
    detail = body.get("detail", "")
    assert "Traceback" not in detail
    assert "traceback" not in detail
    assert "sqlite3" not in detail
