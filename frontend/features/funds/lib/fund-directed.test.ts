import { describe, expect, it } from "vitest";
import { ceilingHint, destinationNote, directedActionLabel, overCeiling, priceNote, shareNote } from "./fund-directed";

// O dinheiro formatado separa "R$" do valor com espaço não separável
const plain = (text: string) => text.replaceAll(" ", " ");

describe("ceilingHint", () => {
  it("com limite de participação diz o teto e a parte que fica com o mercado", () => {
    // Teto de 70% para os gestores deixa 30% para o mercado
    expect(ceilingHint({ room: "18093", manager_cap: "0.7" })).toBe(
      "Seu teto: 18.093 cotas, porque o mercado fica com pelo menos 30% das cotas",
    );
  });

  it("sem limite de participação diz só o espaço da emissão", () => {
    expect(ceilingHint({ room: "35740", manager_cap: null })).toBe("Até 35.740 cotas nesta emissão");
  });

  it("sem teto não há dica", () => {
    expect(ceilingHint({ room: null, manager_cap: null })).toBeNull();
  });
});

describe("overCeiling", () => {
  it("passa do teto só acima do espaço; teto nulo nunca passa", () => {
    expect(overCeiling(18093, "18093")).toBe(false);
    expect(overCeiling(18094, "18093")).toBe(true);
    expect(overCeiling(1_000_000, null)).toBe(false);
  });
});

describe("destinationNote", () => {
  it("com taxa a pagar diz quanto quita e quanto fica no caixa", () => {
    expect(plain(destinationNote("18420", "92020"))).toBe(
      "R$ 18.420,00 quitam antes a taxa a pagar; R$ 92.020,00 ficam no caixa",
    );
  });

  it("sem taxa a pagar diz só o caixa", () => {
    expect(plain(destinationNote("0", "110440"))).toBe("R$ 110.440,00 ficam no caixa");
  });
});

describe("shareNote", () => {
  it("mostra a parte antes e depois sobre o total novo de cotas", () => {
    // 19.590 de 35.740 = 54,8%; 20.590 de 36.740 = 56,0%
    expect(plain(shareNote({ my_share_now: "0.548", my_share_after: "0.56", total_after: "36740" }))).toBe(
      "54,8% → 56,0% de 36.740 cotas",
    );
  });
});

describe("priceNote", () => {
  it("traz os dois preços do dia e o exemplo", () => {
    const text = priceNote({ nav: "110.44", ranking_price: "107.3" });
    expect(plain(text)).toContain("patrimônio por cota (R$ 110,44)");
    expect(plain(text)).toContain("preço de ranking (R$ 107,30)");
    expect(plain(text)).toContain("sairia a R$ 120,00");
  });
});

describe("directedActionLabel", () => {
  it("emite para si e oferece ao co-gestor", () => {
    expect(directedActionLabel(1000, null)).toBe("Emitir 1.000 cotas");
    expect(directedActionLabel(1000, "Duda")).toBe("Oferecer 1.000 cotas a Duda");
  });

  it("sem quantidade o botão fica só com o verbo", () => {
    expect(directedActionLabel(0, null)).toBe("Emitir");
  });
});
