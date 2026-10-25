"""As mensagens de erro que chegam ao navegador saem em português."""

import inspect
import re

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.core import exceptions
from backend.core.exceptions import http_exceptions
from backend.routes import register_routes
from backend.routes.error import UNEXPECTED_ERROR_MESSAGE
from backend.routes.simulation import CreateSimulationRequest

# Palavras que só aparecem em frases em inglês
ENGLISH_WORDS = re.compile(
    r"\b(the|was|were|you|your|not|request|server|could|sent|found|failed)\b",
    re.IGNORECASE,
)


def _default_detail(error_class: type[Exception]) -> str:
    return error_class().detail  # type: ignore[attr-defined]


def _error_classes() -> list[type[Exception]]:
    classes: list[type[Exception]] = []
    for module in (http_exceptions, exceptions):
        for _, cls in inspect.getmembers(module, inspect.isclass):
            if issubclass(cls, http_exceptions.HTTPException) and (
                cls.__module__ == module.__name__
            ):
                classes.append(cls)
    return classes


@pytest.mark.parametrize("error_class", _error_classes(), ids=lambda c: c.__name__)
def test_default_detail_is_portuguese(error_class: type[Exception]) -> None:
    detail = _default_detail(error_class)
    assert not ENGLISH_WORDS.search(detail), detail


def test_error_classes_were_collected() -> None:
    names = {cls.__name__ for cls in _error_classes()}
    assert {"BadGatewayError", "NotFoundError", "InsufficentCashError"} <= names


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()

    @app.post("/create")
    def create(body: CreateSimulationRequest) -> None:
        pass

    @app.get("/boom")
    def boom() -> None:
        raise RuntimeError("levels must be >= 2")

    @app.get("/typed")
    def typed(quantity: int) -> None:
        pass

    register_routes(app)
    return TestClient(app, raise_server_exceptions=False)


VALID_BODY = {
    "name": "Teste",
    "start_date": "2020-01-01",
    "end_date": "2021-01-01",
    "starting_cash": "1000",
    "goal_net_worth": "10000",
    "price_impact_k": 0.1,
    "price_impact_decay_days": 5,
}


def test_missing_field_has_message_and_detail(client: TestClient) -> None:
    body = {k: v for k, v in VALID_BODY.items() if k != "starting_cash"}
    response = client.post("/create", json=body)

    assert response.status_code == 422
    payload = response.json()
    assert payload["message"] == "O campo starting_cash é obrigatório."
    assert payload["detail"] == [
        {
            "loc": ["body", "starting_cash"],
            "msg": "O campo starting_cash é obrigatório.",
            "type": "missing",
        }
    ]


def test_constraint_names_the_limit(client: TestClient) -> None:
    response = client.post("/create", json={**VALID_BODY, "starting_cash": "0"})

    assert response.json()["message"] == (
        "O campo starting_cash precisa ser maior que 0."
    )


def test_project_validator_message_is_kept(client: TestClient) -> None:
    response = client.post(
        "/create",
        json={**VALID_BODY, "start_date": "2022-01-01", "end_date": "2021-01-01"},
    )

    assert response.status_code == 422
    assert response.json()["message"] == "Data de início deve ser antes da data de fim."


def test_query_parsing_error(client: TestClient) -> None:
    response = client.get("/typed", params={"quantity": "abc"})

    assert (
        response.json()["message"] == "O campo quantity precisa ser um número inteiro."
    )


def test_several_failures_are_joined(client: TestClient) -> None:
    body = {k: v for k, v in VALID_BODY.items() if k not in ("name", "starting_cash")}
    message = client.post("/create", json=body).json()["message"]

    assert message == "O campo name é obrigatório. O campo starting_cash é obrigatório."


def test_invalid_json_body(client: TestClient) -> None:
    response = client.post(
        "/create", content="{", headers={"Content-Type": "application/json"}
    )

    assert response.json()["message"] == "O corpo da requisição não é um JSON válido."


def test_unexpected_error_hides_internal_text(client: TestClient) -> None:
    response = client.get("/boom")

    assert response.status_code == 500
    assert response.json() == {"message": UNEXPECTED_ERROR_MESSAGE}


def test_unknown_route_method_is_portuguese(client: TestClient) -> None:
    response = client.post("/boom")

    assert response.status_code == 405
    assert response.json() == {"message": "Este endereço não aceita esse método."}
