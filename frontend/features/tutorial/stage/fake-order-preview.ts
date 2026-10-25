import type { OrderPreview, OrderPreviewRequest } from "@/types";

/** Dados do exemplo: a conta do palco parte de R$ 100.000 em caixa e PETR4 a R$ 38,12. */
export const STAGE_CASH_CENTS = 100_000_00;
export const STAGE_PRICE_CENTS = 38_12;

const money = (cents: number) => (cents / 100).toFixed(2);

/** Prévia da compra de exemplo, calculada em centavos para fechar sem erro de ponto flutuante. */
export function fakeOrderPreview(request: OrderPreviewRequest): OrderPreview {
  const limitCents = request.limit_price != null ? Math.round(request.limit_price * 100) : null;
  const priceCents = limitCents ?? STAGE_PRICE_CENTS;
  const quantity = Math.max(0, Math.floor(Number(request.quantity ?? 0)) || 0);
  const totalCents = quantity * priceCents;

  return {
    price: money(priceCents),
    quantity: String(quantity),
    total: money(totalCents),
    cash_before: money(STAGE_CASH_CENTS),
    cash_after: money(STAGE_CASH_CENTS - totalCents),
    max_quantity: String(Math.floor(STAGE_CASH_CENTS / priceCents)),
    held: "0",
    reserved: "0",
    profit: null,
    tax: null,
    month_sales_after: null,
    exemption_limit: "20000.00",
    tax_due_date: null,
  };
}
