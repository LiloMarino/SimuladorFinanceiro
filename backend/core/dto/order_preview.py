from datetime import date
from decimal import Decimal

from backend.core.dto.base import BaseDTO


class OrderPreviewDTO(BaseDTO):
    """O que uma ordem faria se executasse agora, para a boleta mostrar antes do envio."""

    # Preço estimado: o limite, ou o melhor preço do outro lado do book; sem nenhum, o último fechamento
    price: Decimal | None
    total: Decimal
    cash_before: Decimal
    cash_after: Decimal
    # Compra: o que o caixa paga ao preço estimado; venda: o que está livre de ordens abertas
    max_quantity: Decimal
    held: Decimal
    reserved: Decimal
    # Só na venda: lucro sobre o preço médio e o IR que a venda acrescenta ao mês
    profit: Decimal | None
    tax: Decimal | None
    # Vendas do mês na classe do ativo (ação ou cripto) com esta venda, e o teto da isenção dela
    month_sales_after: Decimal | None
    exemption_limit: Decimal
    tax_due_date: date | None


class TradeDTO(BaseDTO):
    """Uma execução de compra ou venda na sala, lida dos eventos."""

    event_date: date
    player_nickname: str
    # Chave da paleta do jogador nesta partida
    player_color: str
    action: str
    quantity: Decimal
    price: Decimal
