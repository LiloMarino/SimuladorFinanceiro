from datetime import date
from decimal import Decimal

from backend.core.dto.base import BaseDTO


class SovereignOrderPreviewDTO(BaseDTO):
    """O que a compra pelo Fundo Soberano muda na fatia da empresa ou da gestora, para a boleta do fundo."""

    # O nome da empresa ou da gestora dona do ativo
    issuer: str
    is_fund: bool
    # Fatia do fundo no ativo antes e depois da ordem, contando as ordens abertas de compra;
    # nula quando o número de papéis em circulação é desconhecido
    stake_before: Decimal | None
    stake_after: Decimal | None
    ceiling: Decimal
    # Quantos papéis ainda cabem sob o teto, antes desta ordem
    room: Decimal | None
    # Cota de gestora cujo gestor é do partido que governa ou da base: a compra vira favorecimento
    allied: bool
    # Por que o fundo não compra este ativo; nulo quando pode
    refusal: str | None


class OrderPreviewDTO(BaseDTO):
    """O que uma ordem faria se executasse agora, para a boleta mostrar antes do envio."""

    # Preço estimado: o limite, ou o melhor preço do outro lado do book; sem nenhum, o último fechamento
    price: Decimal | None
    # A quantidade pedida; na compra por valor, a que o valor paga ao preço estimado
    quantity: Decimal
    total: Decimal
    cash_before: Decimal
    cash_after: Decimal
    # Compra: o que o caixa paga ao preço estimado; venda: o que está livre de ordens abertas
    max_quantity: Decimal
    held: Decimal
    reserved: Decimal
    # A posição no ativo depois da ordem, e a fração do patrimônio (ativos da conta que opera: ações,
    # renda fixa e caixa) que ela passa a ocupar, ao preço de mercado de hoje
    held_after: Decimal
    networth_share_after: Decimal
    # Só na venda: lucro sobre o preço médio e o IR que a venda acrescenta ao mês
    profit: Decimal | None
    tax: Decimal | None
    # Vendas do mês na classe do ativo (ação ou cripto) com esta venda, e o teto da isenção dela
    month_sales_after: Decimal | None
    exemption_limit: Decimal
    tax_due_date: date | None
    # Só quando a conta que opera é o Fundo Soberano e a ordem é de compra
    sovereign: SovereignOrderPreviewDTO | None = None


class TradeDTO(BaseDTO):
    """Uma execução de compra ou venda na sala, lida dos eventos."""

    event_date: date
    player_nickname: str
    # Chave da paleta do jogador nesta partida
    player_color: str
    action: str
    quantity: Decimal
    price: Decimal
