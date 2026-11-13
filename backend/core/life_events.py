"""
O catálogo de imprevistos de fábrica do viver de renda: família, peso, efeito, valor em
despesas mensais e o texto que cada profissão lê. O catálogo é dado puro: o sorteio
mora no `life_events.py` da simulação e a lista da partida, em `dto/life.py`.

Os pesos dos tipos bons somam 10 dos 40 do catálogo: com as três famílias em Normal,
um imprevisto em cada quatro é bom. O valor esperado do bom fica abaixo do ruim, e o
imprevisto segue sendo, na média, um custo que pede reserva de emergência.
"""

from dataclasses import dataclass, field
from decimal import Decimal

from backend.core.enum import LifeEventEffect, LifeEventFamily, Profession

# O imprevisto de cada profissão que ela vive na própria versão: o sorteio é um só
# para a sala, o efeito e o tamanho são os mesmos para todos
SETBACK_KEY = "SETBACK"
BOOM_KEY = "BOOM"


@dataclass(frozen=True)
class LifeEventSpec:
    key: str
    label: str
    family: LifeEventFamily
    effect: LifeEventEffect
    # Chance relativa entre os tipos quando sai um imprevisto
    weight: int
    # Quantas despesas mensais saem (ou entram) do caixa
    expense_multiple: Decimal
    # O nome do tipo para quem tem a profissão, quando difere do genérico
    by_profession: dict[Profession, str] = field(default_factory=dict)


def _out(
    key: str, label: str, weight: int, multiple: str, **by_profession: str
) -> LifeEventSpec:
    return LifeEventSpec(
        key,
        label,
        LifeEventFamily.EXPENSES,
        LifeEventEffect.CASH_OUT,
        weight,
        Decimal(multiple),
        _texts(by_profession),
    )


def _in(
    key: str, label: str, weight: int, multiple: str, **by_profession: str
) -> LifeEventSpec:
    return LifeEventSpec(
        key,
        label,
        LifeEventFamily.GOOD,
        LifeEventEffect.CASH_IN,
        weight,
        Decimal(multiple),
        _texts(by_profession),
    )


def _texts(by_profession: dict[str, str]) -> dict[Profession, str]:
    return {Profession[name]: text for name, text in by_profession.items()}


LIFE_EVENT_CATALOG: tuple[LifeEventSpec, ...] = (
    # Despesas
    _out("REPAIR", "Conserto do carro", 3, "1"),
    _out("HEALTH", "Despesa de saúde", 2, "2"),
    _out("HOME_REPAIR", "Conserto da casa", 2, "1.5"),
    _out("APPLIANCE", "Eletrodoméstico queimado", 3, "0.75"),
    _out("PHONE", "Celular quebrado", 3, "0.5"),
    _out("TRAFFIC_FINE", "Multa de trânsito", 3, "0.25"),
    _out("VET", "Veterinário", 2, "0.5"),
    _out("DENTIST", "Dentista de urgência", 2, "0.75"),
    _out("CARD_SCAM", "Golpe no cartão", 2, "1"),
    _out("EMERGENCY_TRIP", "Viagem de emergência", 1, "1"),
    _out("CONDO_FEE", "Rateio extra do condomínio", 3, "0.5"),
    _out("RELATIVE_HELP", "Ajuda a um parente", 1, "1"),
    # Renda e emprego
    LifeEventSpec(
        "LAYOFF",
        "Demissão",
        LifeEventFamily.INCOME,
        LifeEventEffect.SKIP_NEXT_SALARY,
        1,
        Decimal(0),
    ),
    LifeEventSpec(
        SETBACK_KEY,
        "Revés da profissão",
        LifeEventFamily.INCOME,
        LifeEventEffect.CASH_OUT,
        2,
        Decimal(1),
        _texts(
            {
                "CLT": "Curso exigido pago do bolso",
                "PUBLIC_SERVANT": "Desconto extra na folha",
                "ENTREPRENEUR": "Máquina quebrada",
                "RETIREE": "Reajuste do plano de saúde",
                "WELFARE": "Ferramenta do bico quebrada",
                "LANDLORD": "Reforma entre inquilinos",
            }
        ),
    ),
    # Eventos bons
    _in("TAX_REFUND", "Restituição do imposto de renda", 2, "1"),
    _in(
        "WORK_BONUS",
        "Bônus do trabalho",
        2,
        "1",
        CLT="PLR",
        PUBLIC_SERVANT="Gratificação",
        ENTREPRENEUR="Cliente pagou adiantado",
        RETIREE="13º adiantado",
        WELFARE="Bico extra",
        LANDLORD="Reajuste do aluguel",
    ),
    _in("RAFFLE", "Prêmio de sorteio", 1, "0.5"),
    _in("SMALL_INHERITANCE", "Herança pequena", 1, "3"),
    _in("USED_SALE", "Venda de um bem usado", 2, "0.75"),
    _in("FAMILY_GIFT", "Presente de família", 1, "0.5"),
    LifeEventSpec(
        BOOM_KEY,
        "Boa fase da profissão",
        LifeEventFamily.GOOD,
        LifeEventEffect.CASH_IN,
        1,
        Decimal(1),
        _texts(
            {
                "CLT": "Hora extra paga",
                "PUBLIC_SERVANT": "Auxílio de função",
                "ENTREPRENEUR": "Contrato grande",
                "RETIREE": "Revisão da aposentadoria",
                "WELFARE": "Cliente novo no bico",
                "LANDLORD": "Multa de rescisão recebida",
            }
        ),
    ),
)

TEXTS_BY_KEY: dict[str, dict[Profession, str]] = {
    spec.key: spec.by_profession for spec in LIFE_EVENT_CATALOG if spec.by_profession
}


def life_event_label(key: str, label: str, profession: Profession | None) -> str:
    """O nome do imprevisto para quem tem a profissão; sem profissão (ou sem texto dela), o nome genérico do tipo."""
    if profession is None:
        return label
    return TEXTS_BY_KEY.get(key, {}).get(profession, label)
