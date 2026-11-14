import { describe, expect, it } from "vitest";
import { cleanTickerLetters, tickerOf } from "./fund-ticker";

describe("sigla da gestora", () => {
  it("o campo limpa o que digitam: maiúsculas, só letras, até quatro", () => {
    expect(cleanTickerLetters("au1ro-x")).toBe("AURO");
    expect(cleanTickerLetters("aurora")).toBe("AURO");
  });

  it("as quatro letras ganham o sufixo 11", () => {
    expect(tickerOf("AURO")).toBe("AURO11");
  });
});
