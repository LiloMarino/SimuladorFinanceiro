import type { QueryClient } from "@tanstack/react-query";
import { queryKeys } from "./queryKeys";

/** Descarta leituras anteriores à pausa e confere o último dia concluído no servidor. */
export async function revalidateSimulation(client: QueryClient) {
  const keys = [
    queryKeys.simulationState(),
    queryKeys.variableIncome(),
    queryKeys.fixedIncome(),
    queryKeys.portfolio(),
    queryKeys.economicIndicators(),
    queryKeys.economyPanel(),
    queryKeys.myStrategy(),
  ];
  await Promise.all(keys.map((queryKey) => client.cancelQueries({ queryKey })));
  await Promise.all(keys.map((queryKey) => client.invalidateQueries({ queryKey })));
}

/** Uma operação na pausa também altera prévias, reservas, caixa, histórico e as ordens abertas que o automático cancelaria. */
export async function revalidateOrder(client: QueryClient, ticker: string) {
  const keys = [
    queryKeys.orderPreview(ticker),
    queryKeys.variableIncomeOrders(ticker),
    queryKeys.trades(ticker),
    queryKeys.portfolio(),
    queryKeys.simulationState(),
    queryKeys.fixedIncome(),
    queryKeys.myStrategy(),
  ];
  await Promise.all(keys.map((queryKey) => client.invalidateQueries({ queryKey })));
}
