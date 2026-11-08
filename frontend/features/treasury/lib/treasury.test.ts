import { format } from "date-fns";
import { describe, expect, it } from "vitest";
import type { TreasuryHistoryPoint } from "@/types";
import {
  baseRateCaption,
  baseShare,
  closingLabel,
  displayGain,
  gaugePosition,
  displayDay,
  displayMonthYear,
  historyRows,
  percentOf,
  pointsOf,
  pointsUnit,
  ratesDate,
  reviewMonthName,
  termLabel,
  treasuryRateLabel,
} from "./treasury";

// O Intl separa "R$" do número com espaço não separável
const plain = (text: string) => text.replace(/ /g, " ");

describe("gaugePosition", () => {
  it("a régua vai de 0% a 150%: 88,7% cai em 59,13% da largura", () => {
    // 0,887 ÷ 1,5 = 0,59133
    expect(gaugePosition(0.887)).toBeCloseTo(59.133, 3);
  });

  it("passando de 150% o marcador fica na ponta", () => {
    expect(gaugePosition(2)).toBe(100);
  });
});

describe("taxa em base e prêmio", () => {
  it("escreve a taxa de cada indexador", () => {
    expect(treasuryRateLabel("SELIC", "0.0244")).toBe("SELIC + 2,44%");
    expect(treasuryRateLabel("IPCA", "0.0945")).toBe("IPCA + 9,45%");
    expect(treasuryRateLabel("Prefixado", "0.1292")).toBe("12,92% ao ano");
  });

  it("a legenda da barra abre a parte base em pontos", () => {
    expect(baseRateCaption("SELIC", "0.001")).toBe("SELIC + 0,10 base +");
    expect(baseRateCaption("Prefixado", "0.1058")).toBe("10,58 base +");
  });

  it("a barra cinza é a base dividida pela taxa inteira", () => {
    // 10,58 ÷ 12,92 = 81,9%
    expect(baseShare("0.1058", "0.1292")).toBeCloseTo(81.9, 1);
    expect(baseShare("0.1118", "0.1118")).toBe(100);
  });

  it("pontos de zero ficam sem casas", () => {
    expect(pointsOf("0.0234")).toBe("2,34");
    expect(pointsOf(0)).toBe("0");
  });
});

describe("displayGain", () => {
  it("mostra o sinal do ganho e da perda", () => {
    expect(plain(displayGain("6682.67"))).toBe("+R$ 6.682,67");
    expect(plain(displayGain("-2416.42"))).toBe("−R$ 2.416,42");
  });

  it("valores de nove dígitos viram a escala curta", () => {
    expect(plain(displayGain("-987700000"))).toBe("−R$ 988 mi");
  });
});

describe("datas do Tesouro", () => {
  it("escreve dia e mês curtos", () => {
    expect(displayDay("2033-03-01")).toBe("1 mar 2033");
    expect(displayMonthYear("2031-12-31")).toBe("dez 2031");
  });

  it("conta o prazo em meses cheios", () => {
    expect(termLabel("2033-03-01", "2030-09-30")).toBe("2 anos e 5 meses");
    expect(termLabel("2037-01-01", "2030-09-30")).toBe("6 anos e 3 meses");
    expect(termLabel("2031-01-01", "2030-09-30")).toBe("3 meses");
    expect(termLabel("2032-03-01", "2030-09-30")).toBe("1 ano e 5 meses");
  });

  it("a taxa vale desde o fechamento anterior e a revisão é no fechamento do mês", () => {
    expect(format(ratesDate("2030-11-01"), "yyyy-MM-dd")).toBe("2030-09-30");
    expect(reviewMonthName("2030-11-01")).toBe("outubro");
  });
});

describe("percentOf", () => {
  it("tira as casas quando o percentual é inteiro", () => {
    expect(percentOf("0.15")).toBe("15%");
    expect(percentOf("0.175")).toBe("17,5%");
  });
});

describe("historyRows", () => {
  const quote = (name: string, rate_index: "Prefixado" | "IPCA", maturity_date: string, effective: string | null) => ({
    name,
    rate_index,
    maturity_date,
    base_rate: "0.1",
    premium: "0.0143",
    effective_annual_rate: effective,
  });
  const point: TreasuryHistoryPoint = {
    month: "2028-04-01",
    selic: "0.1242",
    ipca: "0.046",
    premium: "0.0143",
    debt: "0.77",
    band_index: 1,
    quotes: [
      quote("Tesouro Prefixado 2037", "Prefixado", "2037-01-01", "0.1352"),
      quote("Tesouro Prefixado 2030", "Prefixado", "2030-01-01", "0.117"),
      quote("Tesouro IPCA+ 2032", "IPCA", "2032-05-15", "0.1314"),
    ],
  };

  it("pega o título mais curto de cada indexador e fecha no último dia do mês anterior", () => {
    const [row] = historyRows([point]);
    expect(row).toMatchObject({
      closing: "2028-03-31",
      selic: 0.1242,
      prefixed: 0.117,
      prefixedName: "Prefixado 2030",
      inflation: 0.1314,
      inflationName: "IPCA+ 2032",
      debt: 0.77,
      premium: 0.0143,
    });
  });

  it("sem a dívida do governo e com a taxa equivalente escondida os campos ficam nulos", () => {
    const hidden = { ...point, debt: null, quotes: point.quotes.map((q) => ({ ...q, effective_annual_rate: null })) };
    const [row] = historyRows([hidden]);
    expect(row).toMatchObject({ debt: null, prefixed: null, inflation: null });
  });
});

describe("rótulos do gráfico e do termômetro", () => {
  it("escreve o fechamento como mês e ano curto", () => {
    expect(closingLabel("2028-03-31")).toBe("mar/28");
  });

  it("usa ponto no singular até um ponto inteiro e pontos acima", () => {
    expect([pointsUnit("0.0012"), pointsUnit("0.01"), pointsUnit("0.0234")]).toEqual(["ponto", "ponto", "pontos"]);
  });
});
