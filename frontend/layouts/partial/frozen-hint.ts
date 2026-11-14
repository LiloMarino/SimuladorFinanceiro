import { displayIsoDate } from "@/shared/lib/utils/display";

/** O texto da dica do cadeado: o último dia do congelamento e o que isso significa. */
export function frozenHint(until: string, severalAccounts: boolean) {
  return {
    title: `Congelada até ${displayIsoDate(until)}`,
    body: `Você governa, então ${severalAccounts ? "suas contas ficam paradas" : "sua carteira fica parada"} no mandato: comprar e vender estão bloqueados, e a sala vê o que você tem. Proventos e juros continuam caindo no caixa.`,
  };
}
