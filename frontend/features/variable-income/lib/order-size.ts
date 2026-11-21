import type { OrderPreviewRequest } from "@/types";

type OrderSizeInput = {
  maxChosen: boolean;
  byAmount: boolean;
  quantity: string;
  amount: string;
};

/** O tamanho que a boleta manda ao servidor: o Máx vai como intenção e o servidor conta a quantidade; senão vai o valor ou a quantidade digitados. */
export function orderSizeOf({
  maxChosen,
  byAmount,
  quantity,
  amount,
}: OrderSizeInput): Pick<OrderPreviewRequest, "quantity" | "amount" | "max_size"> {
  if (maxChosen) return { max_size: true };
  return byAmount ? { amount } : { quantity };
}
