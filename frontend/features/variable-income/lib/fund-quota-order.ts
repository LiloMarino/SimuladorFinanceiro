import { premium, quotasToControl, sellableKeepingControl } from "@/shared/lib/fund-quota";

/** Quanto do que o comprador paga é ágio: quantidade × (preço − patrimônio por cota). */
export function premiumPaid(quantity: number, price: number, nav: number) {
  return quantity * (price - nav);
}

/** As cotas e a parte do total que o jogador tem depois de comprar (`issued`: a compra emite cotas novas, como na oferta). */
export function holdingAfterBuy(mine: number, total: number, quantity: number, issued: boolean) {
  const quotas = mine + quantity;
  const totalAfter = issued ? total + quantity : total;
  return { quotas, share: totalAfter > 0 ? quotas / totalAfter : 0 };
}

/** As cotas e a parte do total que o gestor tem depois de vender (a venda só muda de dono, o total fica). */
export function holdingAfterSell(mine: number, total: number, quantity: number) {
  const quotas = Math.max(0, mine - quantity);
  return { quotas, share: total > 0 ? quotas / total : 0 };
}

type QuotaOrderInput = {
  action: "buy" | "sell";
  mine: number;
  total: number;
  /** Patrimônio por cota; nulo antes do primeiro dia da gestora */
  nav: number | null;
  /** Preço por cota da ordem, vindo da prévia */
  price: number;
  quantity: number;
  /** A compra emite cotas novas, como na oferta pública */
  issued: boolean;
  /** Só o gestor principal tem controle a perder */
  manager: boolean;
};

/** O que a ordem de cota faz: o ágio pago, a posição depois e se o gestor perde o controle com a venda. */
export function quotaOrderOutlook(input: QuotaOrderInput) {
  const { action, mine, total, nav, price, quantity, issued, manager } = input;
  const buying = action === "buy";
  const after = buying ? holdingAfterBuy(mine, total, quantity, issued) : holdingAfterSell(mine, total, quantity);
  const hadControl = manager && quotasToControl(mine, total) === 0;
  const hasPremium = buying && nav !== null && price > 0 && quantity > 0;

  return {
    after,
    premiumRate: hasPremium ? premium(price, nav) : null,
    premiumPaid: hasPremium ? premiumPaid(quantity, price, nav) : null,
    losesControl: !buying && hadControl && quotasToControl(after.quotas, total) > 0,
    sellable: sellableKeepingControl(mine, total),
  };
}
