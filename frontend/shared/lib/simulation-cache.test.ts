import { QueryClient, QueryObserver } from "@tanstack/react-query";
import { describe, expect, it } from "vitest";
import { queryKeys } from "./queryKeys";
import { revalidateOrder, revalidateSimulation } from "./simulation-cache";

describe("conferência dos dados na pausa", () => {
  it("renova o estado para cada jogador e marca as listas e detalhes antigos como desatualizados", async () => {
    const clients = [new QueryClient(), new QueryClient()];
    for (const [index, client] of clients.entries()) {
      const observer = new QueryObserver(client, { queryKey: queryKeys.simulationState(),
        queryFn: async () => ({ current_date: "2020-02-03", cash: 100 + index, speed: 0 }), staleTime: Infinity });
      client.setQueryData(queryKeys.simulationState(), { current_date: "2020-01-31", speed: 1 });
      const stop = observer.subscribe(() => {});
      client.setQueryData(queryKeys.fixedIncomeList(), ["oferta antiga"]);
      client.setQueryData(queryKeys.variableIncomeStock("ABCD3"), { history: [] });
      await revalidateSimulation(client);
      expect(client.getQueryData(queryKeys.simulationState())).toEqual({ current_date: "2020-02-03", cash: 100 + index, speed: 0 });
      expect(client.getQueryState(queryKeys.fixedIncomeList())?.isInvalidated).toBe(true);
      expect(client.getQueryState(queryKeys.variableIncomeStock("ABCD3"))?.isInvalidated).toBe(true);
      stop();
      client.clear();
    }
  });

  it("descarta uma resposta em andamento anterior à pausa", async () => {
    const client = new QueryClient();
    let calls = 0;
    let oldSignal: AbortSignal | undefined;
    const observer = new QueryObserver(client, { queryKey: queryKeys.variableIncomeStock("ABCD3"),
      queryFn: ({ signal }) => {
        calls++;
        if (calls === 1) {
          oldSignal = signal;
          return new Promise<string>(() => {});
        }
        return Promise.resolve("dia final conferido");
      } });
    const stop = observer.subscribe(() => {});
    await revalidateSimulation(client);
    expect(oldSignal?.aborted).toBe(true);
    expect(client.getQueryData(queryKeys.variableIncomeStock("ABCD3"))).toBe("dia final conferido");
    stop();
    client.clear();
  });

  it("refaz a prévia depois de uma operação mesmo sem chegar outro tick ou WS", async () => {
    const client = new QueryClient();
    const key = queryKeys.orderPreview("ABCD3", { action: "sell", quantity: 1 });
    client.setQueryData(key, { held: 0, max_quantity: 0 });
    const observer = new QueryObserver(client, { queryKey: key, queryFn: async () => ({ held: 1, max_quantity: 1 }), staleTime: Infinity });
    const stop = observer.subscribe(() => {});
    await revalidateOrder(client, "ABCD3");
    expect(client.getQueryData(key)).toEqual({ held: 1, max_quantity: 1 });
    stop();
    client.clear();
  });
});
