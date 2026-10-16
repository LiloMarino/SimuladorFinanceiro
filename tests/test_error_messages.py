"""As mensagens de erro que chegam ao navegador saem em português."""

import asyncio
import contextlib
import inspect
import json
import re
from dataclasses import dataclass
from typing import Any

import pytest
from fastapi import FastAPI

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


@dataclass
class Response:
    status_code: int
    body: bytes

    def json(self) -> Any:
        return json.loads(self.body)


class Client:
    """Chama o app ASGI direto: o `TestClient` do Starlette pede o pacote httpx2."""

    def __init__(self, app: FastAPI):
        self.app = app

    def request(
        self,
        method: str,
        path: str,
        *,
        json_body: Any = None,
        content: bytes | None = None,
        query: str = "",
    ) -> Response:
        payload = content if content is not None else b""
        if json_body is not None:
            payload = json.dumps(json_body).encode()
        return asyncio.run(self._call(method, path, payload, query))

    async def _call(self, method: str, path: str, payload: bytes, query: str):
        scope = {
            "type": "http",
            "method": method,
            "path": path,
            "query_string": query.encode(),
            "headers": [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(payload)).encode()),
            ],
        }
        sent: list[dict[str, Any]] = []

        async def receive() -> dict[str, Any]:
            return {"type": "http.request", "body": payload, "more_body": False}

        async def send(message: dict[str, Any]) -> None:
            sent.append(message)

        # O ServerErrorMiddleware relança a exceção não tratada depois de responder
        with contextlib.suppress(RuntimeError):
            await self.app(scope, receive, send)  # type: ignore[arg-type]
        status = next(m["status"] for m in sent if m["type"] == "http.response.start")
        body = b"".join(m.get("body", b"") for m in sent)
        return Response(status, body)

    def post(self, path: str, json: Any = None, content: bytes | None = None):
        return self.request("POST", path, json_body=json, content=content)

    def get(self, path: str, params: dict[str, str] | None = None):
        query = "&".join(f"{k}={v}" for k, v in (params or {}).items())
        return self.request("GET", path, query=query)


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
def client() -> Client:
    app = FastAPI()

    @app.post("/create")
    def create(body: CreateSimulationRequest) -> None:  # type: ignore[reportUnusedFunction]
        pass

    @app.get("/boom")
    def boom() -> None:  # type: ignore[reportUnusedFunction]
        raise RuntimeError("levels must be >= 2")

    @app.get("/typed")
    def typed(quantity: int) -> None:  # type: ignore[reportUnusedFunction]
        pass

    register_routes(app)
    return Client(app)


VALID_BODY = {
    "name": "Teste",
    "start_date": "2020-01-01",
    "end_date": "2021-01-01",
    "starting_cash": "1000",
    "price_impact_k": 0.1,
    "price_impact_decay_days": 5,
}


def test_missing_field_has_message_and_detail(client: Client) -> None:
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


def test_constraint_names_the_limit(client: Client) -> None:
    response = client.post("/create", json={**VALID_BODY, "starting_cash": "0"})

    assert response.json()["message"] == (
        "O campo starting_cash precisa ser maior que 0."
    )


def test_project_validator_message_is_kept(client: Client) -> None:
    response = client.post(
        "/create",
        json={**VALID_BODY, "start_date": "2022-01-01", "end_date": "2021-01-01"},
    )

    assert response.status_code == 422
    assert response.json()["message"] == "Data de início deve ser antes da data de fim."


def test_query_parsing_error(client: Client) -> None:
    response = client.get("/typed", params={"quantity": "abc"})

    assert (
        response.json()["message"] == "O campo quantity precisa ser um número inteiro."
    )


def test_several_failures_are_joined(client: Client) -> None:
    body = {k: v for k, v in VALID_BODY.items() if k not in ("name", "starting_cash")}
    message = client.post("/create", json=body).json()["message"]

    assert message == "O campo name é obrigatório. O campo starting_cash é obrigatório."


def test_invalid_json_body(client: Client) -> None:
    response = client.post("/create", content=b"{")

    assert response.json()["message"] == "O corpo da requisição não é um JSON válido."


def test_unexpected_error_hides_internal_text(client: Client) -> None:
    response = client.get("/boom")

    assert response.status_code == 500
    assert response.json() == {"message": UNEXPECTED_ERROR_MESSAGE}


def test_unknown_route_method_is_portuguese(client: Client) -> None:
    response = client.post("/boom")

    assert response.status_code == 405
    assert response.json() == {"message": "Este endereço não aceita esse método."}
