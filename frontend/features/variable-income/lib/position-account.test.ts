import { describe, expect, it } from "vitest";
import { positionEmptyText, positionTitle } from "./position-account";

const manager = { fund_id: 3, name: "Aurora Gestão", role: "manager" } as const;
const sovereign = { fund_id: 0, name: "Fundo Soberano", role: "president" } as const;

describe("positionTitle", () => {
  it("a gestora é 'da' e o Fundo Soberano é 'do'", () => {
    expect(positionTitle(manager)).toBe("Posição da Aurora Gestão");
    expect(positionTitle(sovereign)).toBe("Posição do Fundo Soberano");
  });
});

describe("positionEmptyText", () => {
  it("a gestora é 'A' e o Fundo Soberano é 'O'", () => {
    expect(positionEmptyText(manager, "PETR4")).toBe("A Aurora Gestão não tem PETR4.");
    expect(positionEmptyText(sovereign, "PETR4")).toBe("O Fundo Soberano não tem PETR4.");
  });
});
