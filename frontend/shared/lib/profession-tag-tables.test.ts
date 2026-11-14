import { describe, expect, it } from "vitest";
import { tagTable } from "./profession-tag-tables";

// O formato de moeda usa espaço sem quebra; o teste compara com espaço comum
function rows(table: ReturnType<typeof tagTable>) {
  return table.rows.map(([left, right]) => [left, right.replaceAll(" ", " ")]);
}

describe("tagTable", () => {
  it("PIB do empreendedor: fator 1 + 3 × (PIB − 2%), com piso de 0,5", () => {
    // Renda de 6.000: PIB 4% → 6.000 × 1,06; PIB 0% → 6.000 × 0,94; PIB −15% → fator 0,49 vira 0,5
    expect(rows(tagTable("gdp", "ENTREPRENEUR", 5000))).toEqual([
      ["4%", "R$ 6.360 (+6%)"],
      ["2%", "R$ 6.000"],
      ["0%", "R$ 5.640 (−6%)"],
      ["−15% ou menos", "R$ 3.000 (piso)"],
    ]);
  });

  it("PIB do CLT: IPCA mais metade do PIB, sem reajuste real quando o PIB é negativo", () => {
    // Renda de 5.000 com IPCA de 4%: PIB 4% → 5.000 × (1,04 + 0,02); PIB 2% → 5.000 × 1,05
    expect(rows(tagTable("gdp", "CLT", 5000))).toEqual([
      ["4%", "R$ 5.300"],
      ["2%", "R$ 5.250"],
      ["0% ou menos", "R$ 5.200 (só o IPCA)"],
    ]);
  });

  it("desemprego: 3 imprevistos por ano × 1/40 de demissão × (desemprego ÷ 9%)", () => {
    // 4,5% → 0,0375 por ano → 26,7 anos; 9% → 0,075 → 13,3; 18% → 0,15 → 6,7
    expect(tagTable("unemployment", "CLT", 5000).rows).toEqual([
      ["4,5%", "1 vez a cada 27 anos"],
      ["9%", "1 vez a cada 13 anos"],
      ["18%", "1 vez a cada 7 anos"],
    ]);
  });

  it("IR das pessoas: o desvio da alíquota em pontos multiplica a renda", () => {
    // 5.000 × (1 − (10% − 15%)) = 5.250; 5.000 × (1 − (20% − 15%)) = 4.750
    expect(rows(tagTable("personalTax", "CLT", 5000))).toEqual([
      ["10%", "R$ 5.250 (+5%)"],
      ["15%, a da lei", "R$ 5.000"],
      ["20%", "R$ 4.750 (−5%)"],
    ]);
  });

  it("IR das empresas parte da lei de 34% e o imposto sobre consumo, da de 18%", () => {
    expect(rows(tagTable("corporateTax", "ENTREPRENEUR", 5000))[0]).toEqual(["29%", "R$ 6.300 (+5%)"]);
    // Auxílio: renda de 4.500 × (1 − (23% − 18%))
    expect(rows(tagTable("consumptionTax", "WELFARE", 5000))[2]).toEqual(["23%", "R$ 4.275 (−5%)"]);
  });

  it("gasto com auxílio: 0,4 × salário × gasto ÷ 1,5%, e o bico de 0,5× não muda", () => {
    const table = tagTable("welfareSpending", "WELFARE", 5000);
    expect(rows(table)).toEqual([
      ["0,75% do PIB", "R$ 1.000"],
      ["1,5% do PIB", "R$ 2.000"],
      ["3% do PIB", "R$ 4.000"],
    ]);
    expect(table.footnote.replaceAll(" ", " ")).toBe("O bico, R$ 2.500, não muda.");
  });

  it("aumento dos servidores e dos aposentados: IPCA de 4% mais o aumento sobre a renda de partida", () => {
    // Servidor 4.500 × 1,04 = 4.680; × 1,06 = 4.770; × 1,09 = 4.905
    expect(rows(tagTable("servantRaise", "PUBLIC_SERVANT", 5000))).toEqual([
      ["0%", "R$ 4.680 (só o IPCA)"],
      ["2%", "R$ 4.770"],
      ["5%", "R$ 4.905"],
    ]);
    // Aposentado 4.250 × 1,04 = 4.420
    expect(rows(tagTable("retireeRaise", "RETIREE", 5000))[0]).toEqual(["0%", "R$ 4.420 (só o IPCA)"]);
  });

  it("dólar do Exportador: fator 1 + variação, entre 0,5 e 2", () => {
    // Renda de 5.250 (1,05 × 5.000): +20% → 6.300; −20% → 4.200; +100% bate no teto de 2×; −50% no piso de 0,5×
    expect(rows(tagTable("dollar", "EXPORTER", 5000))).toEqual([
      ["+100% ou mais", "R$ 10.500 (teto)"],
      ["+20%", "R$ 6.300 (+20%)"],
      ["0%", "R$ 5.250"],
      ["−20%", "R$ 4.200 (−20%)"],
      ["−50% ou menos", "R$ 2.625 (piso)"],
    ]);
  });

  it("SELIC do Bancário: fator 1 + 4 × (SELIC − 12%)", () => {
    // Renda de 5.500 (1,1 × 5.000): 16% → 1,16; 8% → 0,84; 20% → 1,32; 4% → 0,68
    expect(rows(tagTable("selic", "BANKER", 5000))).toEqual([
      ["20%", "R$ 7.260 (+32%)"],
      ["16%", "R$ 6.380 (+16%)"],
      ["12%", "R$ 5.500"],
      ["8%", "R$ 4.620 (−16%)"],
      ["4%", "R$ 3.740 (−32%)"],
    ]);
  });

  it("Ibovespa do Corretor: fator 1 + 1,5 × (retorno − 12%), entre 0,4 e 2", () => {
    // Renda de 5.250: +40% → 1,42; 0% → 0,82; −20% → 0,52; −40% → 0,22 vira o piso de 0,4
    expect(rows(tagTable("stocks", "BROKER", 5000))).toEqual([
      ["+40%", "R$ 7.455 (+42%)"],
      ["+12%", "R$ 5.250"],
      ["0%", "R$ 4.305 (−18%)"],
      ["−20%", "R$ 2.730 (−48%)"],
      ["−40% ou menos", "R$ 2.100 (piso)"],
    ]);
  });
});
