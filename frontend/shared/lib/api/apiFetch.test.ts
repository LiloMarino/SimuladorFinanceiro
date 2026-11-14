import { afterEach, describe, expect, it, vi } from "vitest";
import { queryClient } from "@/shared/lib/queryClient";
import { queryKeys } from "@/shared/lib/queryKeys";
import { selectFund } from "@/shared/lib/active-account";
import type { FundAccount } from "@/types";
import { apiFetch } from "./apiFetch";

afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

describe("consultas sem resposta", () => {
  it("encerra o carregamento com erro recuperável quando a leitura demora demais", async () => {
    const timeout = new AbortController();
    vi.spyOn(AbortSignal, "timeout").mockReturnValue(timeout.signal);
    vi.stubGlobal(
      "fetch",
      (_path: string, init: RequestInit) =>
        new Promise<Response>((_resolve, reject) => {
          init.signal?.addEventListener("abort", () => reject(init.signal?.reason));
        }),
    );
    const request = apiFetch("/api/variable-income/ABCD3");
    timeout.abort(new DOMException("Tempo esgotado", "TimeoutError"));
    await expect(request).rejects.toMatchObject({ status: 408 });
  });
  it("preserva cancelamento para que uma consulta antiga não reapareça na pausa", async () => {
    const controller = new AbortController();
    vi.stubGlobal(
      "fetch",
      (_path: string, init: RequestInit) =>
        new Promise<Response>((_resolve, reject) => {
          init.signal?.addEventListener("abort", () => reject(init.signal?.reason));
        }),
    );
    const request = apiFetch("/api/fixed-income", { signal: controller.signal });
    controller.abort();
    await expect(request).rejects.toMatchObject({ name: "AbortError" });
  });
  it("não aplica timeout nem repete automaticamente uma compra", async () => {
    const timeout = vi.spyOn(AbortSignal, "timeout");
    const fetch = vi.fn().mockResolvedValue(new Response(null, { status: 204 }));
    vi.stubGlobal("fetch", fetch);
    await apiFetch("/api/fixed-income/id/buy", { method: "POST", body: { quantity: "100" } });
    expect(timeout).not.toHaveBeenCalled();
    expect(fetch).toHaveBeenCalledTimes(1);
  });
});

describe("conta da gestora", () => {
  const aurora = { fund_id: 3 } as FundAccount;

  async function sentHeaders(init: Parameters<typeof apiFetch>[1]) {
    const fetch = vi.fn().mockResolvedValue(new Response(null, { status: 204 }));
    vi.stubGlobal("fetch", fetch);
    queryClient.setQueryData(queryKeys.simulationStatus(), { simulation: { id: 1, funds_enabled: true } });
    queryClient.setQueryData(queryKeys.fundAccounts(), [{ fund_id: null } as FundAccount, aurora]);
    selectFund(1, 3);
    await apiFetch("/api/portfolio", init);
    const sent = fetch.mock.calls[0]?.[1] as RequestInit;
    return sent.headers;
  }

  afterEach(() => {
    selectFund(1, null);
    queryClient.clear();
  });

  it("só a chamada que pede a conta em uso leva o X-Account", async () => {
    expect(await sentHeaders({ activeAccount: true })).toMatchObject({ "X-Account": "3" });
  });

  it("sem o pedido a chamada é da carteira pessoal, mesmo com a gestora escolhida", async () => {
    expect(await sentHeaders({})).not.toHaveProperty("X-Account");
  });
});
