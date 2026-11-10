import { describe, expect, it } from "vitest";
import { addToContribution } from "./contribution";

// O Intl separa "R$" do número com espaço não separável
const plain = (text: string) => text.replace(/ /g, " ");

describe("addToContribution", () => {
  it("soma o atalho ao valor digitado", () => {
    expect(plain(addToContribution("R$ 2.000,00", 5000))).toBe("R$ 7.000,00");
  });

  it("num campo vazio, o atalho vira o valor", () => {
    expect(plain(addToContribution("", 10000))).toBe("R$ 10.000,00");
  });

  it("atalhos seguidos acumulam", () => {
    const once = addToContribution("", 5000);
    expect(plain(addToContribution(once, 5000))).toBe("R$ 10.000,00");
  });
});
