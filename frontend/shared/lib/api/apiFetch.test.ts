import { afterEach, describe, expect, it, vi } from "vitest";
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
