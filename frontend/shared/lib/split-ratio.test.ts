import { describe, expect, it } from "vitest";
import { describeSplit } from "./split-ratio";

describe("describeSplit", () => {
  it("razão acima de 1 é desdobramento", () => {
    expect(describeSplit("2")).toEqual({ kind: "split", name: "Desdobramento", label: "2 para 1" });
  });

  it("razão abaixo de 1 é grupamento, lido no sentido de quem agrupa", () => {
    expect(describeSplit("0.1")).toEqual({ kind: "reverse", name: "Grupamento", label: "10 para 1" });
  });

  it("razão fracionária vira a menor fração", () => {
    expect(describeSplit("1.5").label).toBe("3 para 2");
    expect(describeSplit("0.6666666667").label).toBe("3 para 2");
  });
});
