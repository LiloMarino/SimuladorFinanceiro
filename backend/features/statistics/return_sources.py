"""De onde veio o retorno de um jogador: valorização, proventos, juro, impostos e custos."""

from decimal import Decimal

from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.dto.return_flows import ReturnFlowsDTO
from backend.core.dto.statistics_report import ReturnSourcesDTO


def build_return_sources(
    last: PatrimonialHistoryDTO,
    capital_provided: Decimal,
    income_tax: Decimal,
    flows: ReturnFlowsDTO,
) -> ReturnSourcesDTO:
    """
    Parte o retorno (patrimônio final menos capital aportado) nas fontes que o caixa
    e a renda fixa registram. A valorização é o resto: as seis parcelas somam o
    retorno por construção, e ela absorve a variação de preço dos ativos e o que
    nenhum evento registra.
    """
    total = last.total_networth - capital_provided
    dividends = flows.dividends
    # Juro bruto da renda fixa: o que está aplicado hoje, mais o que já foi resgatado,
    # menos o que entrou
    fixed_income_interest = last.total_fixed + flows.fixed_redeemed - flows.fixed_bought
    taxes = -(income_tax + flows.fixed_tax_withheld)
    # O principal do empréstimo entra e sai do patrimônio sem efeito: o custo é o que
    # as parcelas pagaram além dele (dívida ainda aberta incluída), mais o cheque especial
    principal_repaid = flows.loan_proceeds - last.total_debt
    debt_interest = -(flows.loan_payment - principal_repaid + flows.overdraft_interest)
    campaign = -flows.campaign
    appreciation = (
        total - dividends - fixed_income_interest - taxes - debt_interest - campaign
    )
    return ReturnSourcesDTO(
        appreciation=appreciation,
        dividends=dividends,
        fixed_income_interest=fixed_income_interest,
        taxes=taxes,
        debt_interest=debt_interest,
        campaign=campaign,
    )
