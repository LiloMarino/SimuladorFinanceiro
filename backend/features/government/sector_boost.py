"""
O empurrão que o governo dá ao preço das ações de um setor (ou segmento): a isenção do IR,
a obra com endereço e a emenda com endereço. Cada fonte sobe em linha reta nos primeiros 6
meses e a soma das três tem teto. Tudo aqui é função pura; o resultado é a alta em fração
(0.05 = ações 5% mais caras), que o preço da partida soma a 1.
"""

from collections.abc import Iterable
from datetime import date
from decimal import Decimal

from backend.core.dto.portfolio import PortfolioDTO
from backend.core.periods import DAYS_PER_MONTH
from backend.features.government.deals import Deal

# Cada fonte chega ao valor cheio em 6 meses, em linha reta
RAMP_MONTHS = 6.0

# A isenção do IR do setor levanta o preço das ações dele em 10%
SECTOR_EXEMPT_BOOST = 0.10

# Obras com endereço: a alta é o gasto em fração do PIB vezes 2,5, até 7,5% (obras de
# 0,7% do PIB dão 1,75%; de 3%, 7,5%)
WORKS_BOOST_SCALE = 2.5
WORKS_BOOST_CAP = 0.075

# Emenda com endereço: a alta é a emenda em fração do PIB por ano vezes 30, até 6% (0,1% do
# PIB dá 3%)
AMENDMENT_BOOST_SCALE = 30.0
AMENDMENT_BOOST_CAP = 0.06

# Isenção, obra e emendas somadas: a alta do setor não passa de 20%
SECTOR_BOOST_CAP = 0.20

# Favorecimento: cada fatia inteira da carteira do presidente no setor da obra tira 6
# pontos do alvo de aprovação de todos os grupos (fatia de 0,40 tira 2,4)
FAVORITISM_POINTS = Decimal(6)


def ramp(since: date, day: date) -> float:
    """Quanto da alta cheia já vale em `day`: 0 no primeiro dia, 1 depois de 6 meses."""
    months = (day - since).days / float(DAYS_PER_MONTH)
    return max(0.0, min(1.0, months / RAMP_MONTHS))


def exemption_boost(since: date | None, day: date) -> float:
    """A alta da isenção que vale desde `since`; sem isenção no dia, zero."""
    return 0.0 if since is None else SECTOR_EXEMPT_BOOST * ramp(since, day)


def works_peak(value: Decimal) -> float:
    """A alta cheia de uma obra de `value` do PIB por ano."""
    return min(WORKS_BOOST_CAP, float(value) * WORKS_BOOST_SCALE)


def works_boost(works: tuple[date, Decimal] | None, day: date) -> float:
    """A alta da obra com endereço: o dia desde o qual ela aponta para o alvo e o valor dela no dia."""
    if works is None:
        return 0.0
    since, value = works
    return works_peak(value) * ramp(since, day)


def amendment_peak(ratio: Decimal) -> float:
    """A alta cheia de uma emenda de `ratio` do PIB por ano."""
    return min(AMENDMENT_BOOST_CAP, float(ratio) * AMENDMENT_BOOST_SCALE)


def amendment_boost(
    deals: Iterable[Deal], sector: str, segment: str, day: date
) -> float:
    """A soma da alta das emendas com endereço que valem em `day`; o acordo só com setor vale para todos os segmentos dele."""
    total = 0.0
    for deal in deals:
        if (
            deal.sector == sector
            and deal.segment in (None, segment)
            and deal.ramp_start is not None
            and deal.covers(day)
        ):
            total += amendment_peak(deal.ratio) * ramp(deal.ramp_start, day)
    return total


def as_fraction(boost: float) -> Decimal:
    """A alta como fração exata para o painel, com 4 casas (0.0175 = 1,75%)."""
    return Decimal(str(round(boost, 4)))


def combined(exemption: float, works: float, amendments: float) -> float:
    """A alta total do setor: as três fontes somadas, limitadas a 20%."""
    return min(SECTOR_BOOST_CAP, exemption + works + amendments)


def favoritism_points(stake: Decimal) -> Decimal:
    """Os pontos de aprovação que a obra direcionada custa a todos os grupos, dada a fatia do presidente no setor."""
    return FAVORITISM_POINTS * stake


def portfolio_share(
    portfolio: PortfolioDTO, sector: str, segment: str | None
) -> Decimal:
    """
    A fatia da carteira (caixa, renda variável e renda fixa a valor de mercado) que está
    nas ações do setor, ou só do segmento quando ele vem; de 0 a 1.
    """
    total = (
        portfolio.cash + portfolio.variable_income_value + portfolio.fixed_income_value
    )
    if total <= 0:
        return Decimal(0)
    held = Decimal(0)
    for allocation in portfolio.sectors:
        if allocation.sector != sector:
            continue
        if segment is None:
            held += allocation.value
        else:
            held += sum(
                (s.value for s in allocation.segments if s.segment == segment),
                Decimal(0),
            )
    return held / total


def computer_sector(abbr: str, sectors: Iterable[str]) -> str | None:
    """O setor que o partido do computador escolhe para a emenda: o da soma dos códigos da sigla, entre os setores em ordem alfabética."""
    names = sorted(set(sectors))
    if not names:
        return None
    return names[sum(ord(c) for c in abbr) % len(names)]
