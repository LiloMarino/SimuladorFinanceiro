from dataclasses import dataclass
from decimal import ROUND_FLOOR, Decimal

from backend.core.life_budget import cents


def exchange_ratio(daughter_nav: Decimal, mother_nav: Decimal) -> Decimal:
    """Cotas da incorporadora por cota da incorporada: o PL por cota de uma sobre o da outra.

    Com a incorporada a R$ 50 e a incorporadora a R$ 100, a razão é 0,5: 2 cotas da primeira
    viram 1 da segunda.
    """
    return daughter_nav / mother_nav


def circular_navs(
    mother_assets: Decimal,
    daughter_assets: Decimal,
    mother_quotas: Decimal,
    daughter_quotas: Decimal,
    mother_in_daughter: Decimal,
    daughter_in_mother: Decimal,
) -> tuple[Decimal, Decimal] | None:
    """O PL por cota de cada gestora quando uma tem cotas da outra na carteira: (incorporadora, incorporada).

    `*_assets` é o patrimônio líquido da carteira sem as cotas da outra gestora. Uma cota
    da outra vale o PL por cota dela, e esse PL por cota depende do da primeira: as duas
    equações se resolvem juntas. Com a incorporadora em R$ 1.000 de patrimônio sem as cotas
    da outra e 10 cotas, a incorporada em R$ 500 e 10 cotas (R$ 50 cada), e a incorporadora com
    2 cotas da incorporada, o PL por cota da incorporadora é (1.000 x 10 + 2 x 500) / (10 x 10)
    = R$ 110: os R$ 1.000 mais as 2 cotas a R$ 50, sobre as 10 cotas. Sem cotas
    cruzadas é o patrimônio sobre as cotas. Nulo quando as duas só têm cotas uma da outra.
    """
    denominator = (
        mother_quotas * daughter_quotas - mother_in_daughter * daughter_in_mother
    )
    if mother_quotas <= 0 or daughter_quotas <= 0 or denominator <= 0:
        return None
    mother_nav = (
        mother_assets * daughter_quotas + mother_in_daughter * daughter_assets
    ) / denominator
    daughter_nav = (
        daughter_assets * mother_quotas + daughter_in_mother * mother_assets
    ) / denominator
    return mother_nav, daughter_nav


def converted_quotas(quotas: Decimal, ratio: Decimal) -> Decimal:
    """As cotas inteiras da incorporadora que `quotas` cotas da incorporada viram."""
    return (quotas * ratio).to_integral_value(rounding=ROUND_FLOOR)


def conversion_remainder(
    quotas: Decimal, daughter_nav: Decimal, converted: Decimal, mother_nav: Decimal
) -> Decimal:
    """Em dinheiro, o que sobra da troca por não caber numa cota inteira: o valor das cotas entregues menos o das recebidas."""
    return max(Decimal(0), cents(quotas * daughter_nav - converted * mother_nav))


def exit_price(daughter_nav: Decimal) -> Decimal:
    """O preço por cota de quem vota contra na incorporada: o PL por cota do dia, em centavos."""
    return cents(daughter_nav)


@dataclass(frozen=True)
class MergeExit:
    """A saída de um cotista que votou contra na incorporada."""

    user_id: int
    quotas: Decimal
    amount: Decimal


@dataclass(frozen=True)
class MergeCash:
    """Como o caixa paga a saída de quem votou contra."""

    # Total a pagar a quem sai
    total: Decimal
    # O que o caixa da incorporada paga, e o que a incorporadora completa logo depois
    from_daughter: Decimal
    from_mother: Decimal
    # O que os dois caixas somados não cobrem; positivo trava a fusão
    shortfall: Decimal


def settle_exits(
    total: Decimal, daughter_cash: Decimal, mother_cash: Decimal
) -> MergeCash:
    """O caixa da incorporada paga primeiro; a incorporadora completa o que faltar do próprio."""
    from_daughter = min(total, max(Decimal(0), daughter_cash))
    from_mother = total - from_daughter
    shortfall = max(Decimal(0), from_mother - max(Decimal(0), mother_cash))
    return MergeCash(
        total=total,
        from_daughter=from_daughter,
        from_mother=from_mother - shortfall,
        shortfall=shortfall,
    )


@dataclass(frozen=True)
class MergeValuation:
    """O PL por cota das duas gestoras e as cotas que uma tem da outra na carteira."""

    # Nulos sem PL por cota
    mother_nav: Decimal | None
    daughter_nav: Decimal | None
    cancelled_daughter_quotas: Decimal
    cancelled_mother_quotas: Decimal


@dataclass(frozen=True)
class MergePlan:
    """O que a fusão faz com os números de agora: a troca de cotas e a saída de quem votou contra."""

    mother_nav: Decimal | None
    daughter_nav: Decimal | None
    # Nulo sem PL por cota nas duas gestoras
    ratio: Decimal | None
    exits: list[MergeExit]
    cash: MergeCash
    # As cotas que uma gestora tem da outra na carteira: a fusão as cancela
    cancelled_daughter_quotas: Decimal
    cancelled_mother_quotas: Decimal

    @property
    def exit_quotas(self) -> Decimal:
        return sum((e.quotas for e in self.exits), Decimal(0))
