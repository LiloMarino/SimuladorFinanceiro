import { QueryClient, QueryObserver } from "@tanstack/react-query";
import { describe, expect, it } from "vitest";
import { createReconnectTracker, refetchSinceDisconnect } from "./refetch-on-reconnect";

describe("acompanhamento da reconexão", () => {
  it("a primeira conexão não é reconexão", () => {
    const track = createReconnectTracker(() => 1000);
    expect(track(false)).toBeNull();
    expect(track(true)).toBeNull();
  });

  it("depois de uma queda, a volta informa o instante em que o socket caiu", () => {
    let now = 1000;
    const track = createReconnectTracker(() => now);
    track(true);
    now = 2000;
    track(false);
    now = 3000;
    expect(track(true)).toBe(2000);
    expect(track(true)).toBeNull();
  });
});

describe("leitura depois da queda do socket", () => {
  it("lê uma vez a consulta ativa anterior à queda e deixa a recente como está", async () => {
    const client = new QueryClient();
    const reads = { old: 0, fresh: 0 };
    const observe = (name: "old" | "fresh") =>
      new QueryObserver(client, {
        queryKey: [name],
        queryFn: async () => ++reads[name],
        staleTime: Infinity,
      }).subscribe(() => {});
    const stops = [observe("old"), observe("fresh")];
    await new Promise((resolve) => setTimeout(resolve, 5));
    const lostAt = Date.now();
    await new Promise((resolve) => setTimeout(resolve, 10));
    // A leitura recente chegou depois da queda (aviso aplicado após a volta)
    client.setQueryData(["fresh"], 99);
    const before = { ...reads };

    await refetchSinceDisconnect(client, lostAt);

    expect(reads.old).toBe(before.old + 1);
    expect(reads.fresh).toBe(before.fresh);
    expect(client.getQueryData(["fresh"])).toBe(99);
    stops.forEach((stop) => stop());
  });
});
