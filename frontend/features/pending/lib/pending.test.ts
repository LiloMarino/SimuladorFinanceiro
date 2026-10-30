import { describe, expect, it } from "vitest";
import type { Pending } from "@/types";
import { bornSince, menuDotSeverity, pendingTarget, severeCount, severeLabel } from "./pending";

function pending(overrides: Partial<Pending>): Pending {
  return {
    key: "CASH_SHORT",
    type: "CASH_SHORT",
    severity: "WARNING",
    title: "Caixa não cobre a próxima parcela",
    detail: "Faltam R$ 920,00 até 05/04",
    resolves: "Some quando o caixa cobre; no vencimento, vira atraso",
    loan_id: null,
    ...overrides,
  };
}

describe("pendingTarget", () => {
  it("leva o pagamento do atraso ao empréstimo da pendência", () => {
    const item = pending({ type: "OVERDUE_INSTALLMENT", loan_id: "abc" });

    expect(pendingTarget(item)).toEqual({ label: "Pagar", to: "/credit?pagar=abc" });
  });

  it("abre o diálogo de hoje na página da eleição", () => {
    expect(pendingTarget(pending({ type: "VICE_INVITE" }))).toEqual({
      label: "Responder",
      to: "/election",
      state: { dialog: "vice" },
    });
    expect(pendingTarget(pending({ type: "CAMPAIGN_OPEN" })).state).toEqual({ dialog: "campaign" });
  });
});

describe("severeCount", () => {
  it("conta só as graves", () => {
    const items = [
      pending({ key: "a", severity: "SEVERE" }),
      pending({ key: "b", severity: "WARNING" }),
      pending({ key: "c", severity: "SEVERE" }),
    ];

    expect(severeCount(items)).toBe(2);
    expect(severeLabel(2)).toBe("2 graves");
    expect(severeLabel(1)).toBe("1 grave");
  });
});

describe("bornSince", () => {
  it("devolve as chaves que a leitura anterior não tinha", () => {
    const items = [pending({ key: "a" }), pending({ key: "b" })];

    expect(bornSince(new Set(["a"]), items).map((item) => item.key)).toEqual(["b"]);
  });
});

describe("menuDotSeverity", () => {
  const items = [
    pending({ key: "a", type: "VICE_INVITE", severity: "WARNING" }),
    pending({ key: "b", type: "IMPEACHMENT_RISK", severity: "SEVERE" }),
  ];

  it("some sem pendência dos tipos do item", () => {
    expect(menuDotSeverity(items, ["STRATEGY_ERROR"])).toBeUndefined();
    expect(menuDotSeverity(undefined, ["VICE_INVITE"])).toBeUndefined();
  });

  it("é âmbar quando só há avisos e vermelho quando alguma é grave", () => {
    expect(menuDotSeverity(items, ["VICE_INVITE", "CAMPAIGN_OPEN"])).toBe("WARNING");
    expect(menuDotSeverity(items, ["IMPEACHMENT_RISK", "VICE_INVITE"])).toBe("SEVERE");
  });
});
