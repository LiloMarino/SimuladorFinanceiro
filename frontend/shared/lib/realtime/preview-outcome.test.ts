import { beforeEach, describe, expect, it, vi } from "vitest";
import ApiError from "@/shared/lib/models/ApiError";
import { fetchPreviewOutcome, outcomeOfPreviewEvent } from "./preview-outcome";

const apiFetch = vi.hoisted(() => vi.fn());
vi.mock("@/shared/lib/api/apiFetch", () => ({ apiFetch }));

describe("fetchPreviewOutcome", () => {
  beforeEach(() => {
    apiFetch.mockReset();
  });

  it("devolve a prévia quando a leitura responde", async () => {
    apiFetch.mockResolvedValue({ quantity: "10" });

    expect(await fetchPreviewOutcome("/api/x")).toEqual({ preview: { quantity: "10" }, refused: null });
  });

  it.each([409, 422])("a recusa de regra (%i) vira dado da prévia", async (status) => {
    apiFetch.mockImplementation(() => Promise.reject(new ApiError("Caixa insuficiente", status, null)));

    expect(await fetchPreviewOutcome("/api/x")).toEqual({ preview: null, refused: "Caixa insuficiente" });
  });

  it.each([400, 401, 403, 404, 500, 503, 0])("o status %i segue como erro da consulta", async (status) => {
    apiFetch.mockImplementation(() => Promise.reject(new ApiError("falhou", status, null)));

    await expect(fetchPreviewOutcome("/api/x")).rejects.toMatchObject({ status });
  });

  it("o erro que não é da API segue como erro da consulta", async () => {
    apiFetch.mockImplementation(() => Promise.reject(new TypeError("falha")));

    await expect(fetchPreviewOutcome("/api/x")).rejects.toBeInstanceOf(TypeError);
  });

  it("repassa o caminho e as opções da leitura", async () => {
    apiFetch.mockResolvedValue({});
    const init = { method: "POST", body: { a: 1 }, activeAccount: true } as const;

    await fetchPreviewOutcome("/api/x", init);

    expect(apiFetch).toHaveBeenCalledWith("/api/x", init);
  });
});

describe("outcomeOfPreviewEvent", () => {
  it("leva a prévia ou o motivo da recusa", () => {
    expect(outcomeOfPreviewEvent({ preview: null, refused: "Não cabe" })).toEqual({
      preview: null,
      refused: "Não cabe",
    });
  });
});
