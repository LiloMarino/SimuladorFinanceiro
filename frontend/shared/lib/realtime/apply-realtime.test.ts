import { QueryClient, QueryObserver } from "@tanstack/react-query";
import { describe, expect, it } from "vitest";
import { applyRealtime, applyRealtimeDelta } from "./apply-realtime";

const key = ["dado"];

const observe = (client: QueryClient, queryFn: () => Promise<unknown>) => {
  const observer = new QueryObserver(client, { queryKey: key, queryFn, staleTime: Infinity });
  return observer.subscribe(() => {});
};

const settle = () => new Promise((resolve) => setTimeout(resolve, 0));

describe("aplicação dos avisos do websocket", () => {
  it("o aviso vale mais que a leitura que saiu antes dele", async () => {
    const client = new QueryClient();
    client.setQueryData(key, "antigo");
    let release: (value: string) => void = () => {};
    const stop = observe(
      client,
      () =>
        new Promise<string>((resolve) => {
          release = resolve;
        }),
    );
    void client.invalidateQueries({ queryKey: key });
    await applyRealtime(client, key, "do aviso");
    release("da leitura");
    await settle();
    expect(client.getQueryData(key)).toBe("do aviso");
    stop();
  });

  it("acrescenta ao dado que a tela já tem", async () => {
    const client = new QueryClient();
    client.setQueryData(key, [1, 2]);
    await applyRealtimeDelta<number[]>(client, key, (current) => [...current, 3]);
    expect(client.getQueryData(key)).toEqual([1, 2, 3]);
  });

  it("lê de novo quando o aviso não encaixa no que a tela tem", async () => {
    const client = new QueryClient();
    client.setQueryData(key, [1]);
    const stop = observe(client, async () => [1, 2, 3, 4]);
    await applyRealtimeDelta<number[]>(client, key, () => null);
    await settle();
    expect(client.getQueryData(key)).toEqual([1, 2, 3, 4]);
    stop();
  });

  it("sem dado base e sem leitura em voo, o aviso é ignorado", async () => {
    const client = new QueryClient();
    await applyRealtimeDelta<number[]>(client, key, (current) => [...current, 3]);
    expect(client.getQueryData(key)).toBeUndefined();
  });

  it("sem dado base e com a primeira leitura em voo, a leitura é refeita", async () => {
    const client = new QueryClient();
    let reads = 0;
    const stop = observe(client, async () => {
      reads += 1;
      return reads;
    });
    await applyRealtimeDelta<number>(client, key, (current) => current + 100);
    await settle();
    expect(reads).toBeGreaterThanOrEqual(2);
    expect(client.getQueryData(key)).toBe(reads);
    stop();
  });
});
