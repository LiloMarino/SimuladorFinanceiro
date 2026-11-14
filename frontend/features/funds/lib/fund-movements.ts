import type { FundDetails } from "@/types";
import { displayMoney, displayQuantity } from "@/shared/lib/utils/display";

type Movement = FundDetails["movements"][number];

/** A frase de cada tipo de movimento da gestora, com os números que ele traz. */
export function movementText(movement: Movement): string {
  const quotas = movement.quotas === null ? "" : `${displayQuantity(movement.quotas)} cotas`;
  const amount = movement.amount === null ? "" : displayMoney(movement.amount);
  const asset = movement.ticker ?? "ativo";

  switch (movement.type) {
    case "contribution":
      return `Integralização: ${amount} da carteira viraram ${quotas}`;
    case "offer_opened":
      return `Oferta pública aberta: ${quotas} ao preço de ${movement.price === null ? "—" : displayMoney(movement.price)}`;
    case "offer_closed":
      return `Oferta pública encerrada: ${quotas} vendidas`;
    case "management_fee":
      return `Taxa de administração de ${amount}`;
    case "performance_fee":
      return `Taxa de performance de ${amount}`;
    case "report_published":
      return "Relatório mensal publicado";
    case "manager_buy":
      return `O gestor comprou ${movement.quotas === null ? "" : `${displayQuantity(movement.quotas)} de `}${asset}`;
    case "manager_sell":
      return `O gestor vendeu ${movement.quotas === null ? "" : `${displayQuantity(movement.quotas)} de `}${asset}`;
  }
}
