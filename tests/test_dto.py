from __future__ import annotations

from decimal import Decimal

from backend.core.dto.economic_indicators import EconomicIndicatorsDTO


def test_decimal_serializes_as_exact_string():
    """Decimal atravessa o JSON como string, com todos os dígitos e sem float."""
    payload = EconomicIndicatorsDTO(
        ipca=Decimal("1234.567891"), selic=Decimal("0.15"), cdi=Decimal("0.149")
    ).to_json()

    assert payload["ipca"] == "1234.567891"
