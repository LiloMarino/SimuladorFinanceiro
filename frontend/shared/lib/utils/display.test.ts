import { describe, expect, it } from "vitest";
import {
  displayBytes,
  displayCompactNumber,
  displayDate,
  displayDecimal,
  displayDuration,
  displayIsoDate,
  displayList,
  displayMoney,
  displayMoneyCompact,
  displayMoneyLarge,
  displayMoneyWhole,
  displayMonthName,
  displayMonthShort,
  displayMonthSlashYear,
  displayNumber,
  displayPercent,
  displayPercentagePoints,
  displayQuantity,
  displayRateLabel,
  displayShortDate,
  displayShortMonthYear,
  displaySignedMoney,
  displaySignedPercent,
  isLoss,
  toCentsString,
} from "./display";

// O Intl separa "R$" do número com espaço não separável
const NBSP = " ";

describe("dinheiro", () => {
  it("duas casas, milhar com ponto e vírgula decimal", () => {
    expect(displayMoney("1234.567891")).toBe(`R$${NBSP}1.234,57`);
    expect(displayMoney(0)).toBe(`R$${NBSP}0,00`);
  });

  it("escala do orçamento: trilhões e bilhões com 3 algarismos", () => {
    expect(displayMoneyLarge(5.76e12)).toBe("R$ 5,76 tri");
    expect(displayMoneyLarge(7.4e12)).toBe("R$ 7,4 tri");
    expect(displayMoneyLarge(110e9)).toBe("R$ 110 bi");
  });

  it("escala do orçamento: o déficit leva o menos tipográfico e o que passa de mil bilhões vira trilhão", () => {
    expect(displayMoneyLarge(-27.2e9)).toBe("−R$ 27,2 bi");
    expect(displayMoneyLarge(999e9)).toBe("R$ 999 bi");
    expect(displayMoneyLarge(1000e9)).toBe("R$ 1 tri");
  });

  it("escala do orçamento: abaixo de um milhão são reais inteiros", () => {
    expect(displayMoneyLarge(0)).toBe(`R$${NBSP}0`);
    expect(displayMoneyLarge(-950000)).toBe(`−R$${NBSP}950.000`);
  });

  it("inteiro e compacto", () => {
    expect(displayMoneyWhole(930200)).toBe(`R$${NBSP}930.200`);
    expect(displayMoneyCompact(1500000)).toBe(`R$${NBSP}1,5${NBSP}mi`);
  });

  it("com sinal usa o menos tipográfico", () => {
    expect(displaySignedMoney("-2340")).toBe(`−R$${NBSP}2.340,00`);
    expect(displaySignedMoney("2340")).toBe(`R$${NBSP}2.340,00`);
  });

  it("centavos para a API, truncados e com ponto", () => {
    expect(toCentsString("1234.569")).toBe("1234.56");
    expect(toCentsString("10")).toBe("10.00");
  });

  it("perda é o valor negativo", () => {
    expect(isLoss(" -1.00")).toBe(true);
    expect(isLoss("1.00")).toBe(false);
  });
});

describe("percentuais", () => {
  it("a fração vira percentual", () => {
    expect(displayPercent("0.11")).toBe("11,00%");
    expect(displayPercent(0.1234, 1)).toBe("12,3%");
  });

  it("com sinal, exceto no zero", () => {
    expect(displaySignedPercent(0.0141)).toBe("+1,41%");
    expect(displaySignedPercent(-0.0141)).toBe("-1,41%");
    expect(displaySignedPercent(0)).toBe("0,00%");
  });

  it("pontos percentuais", () => {
    expect(displayPercentagePoints(0.041)).toBe("+4,10 p.p.");
    expect(displayPercentagePoints(0)).toBe("0,00 p.p.");
  });

  it("taxa da renda fixa", () => {
    expect(displayRateLabel("CDI", "1.1")).toBe("110,00% do CDI");
    expect(displayRateLabel("IPCA", "0.055")).toBe("IPCA + 5,50%");
  });
});

describe("números", () => {
  it("casas fixas, decimal sem zeros sobrando e compacto", () => {
    expect(displayNumber("0.5432")).toBe("0,54");
    expect(displayNumber(1234.5, 0)).toBe("1.235");
    expect(displayDecimal(0.02)).toBe("0,02");
    expect(displayDecimal(1234.5)).toBe("1234,5");
    expect(displayCompactNumber(48200000)).toBe(`48,2${NBSP}mi`);
  });

  it("duração em cada faixa", () => {
    expect(displayDuration(2.5)).toBe("2,5 ms");
    expect(displayDuration(38)).toBe("38 ms");
    expect(displayDuration(11800)).toBe("11,8 s");
    expect(displayDuration(91000)).toBe("1 min 31 s");
    expect(displayDuration(8040000)).toBe("2 h 14 min");
  });

  it("tamanho em cada faixa", () => {
    expect(displayBytes(80)).toBe("80 B");
    expect(displayBytes(5200)).toBe("5,2 KB");
    expect(displayBytes(120000)).toBe("120 KB");
    expect(displayBytes(1550000)).toBe("1,55 MB");
  });
});

describe("datas", () => {
  it("a data ISO é lida no fuso local", () => {
    expect(displayIsoDate("2020-01-02")).toBe("02/01/2020");
    expect(displayDate(new Date(2020, 0, 2))).toBe("02/01/2020");
    expect(displayShortDate("2023-03-14")).toBe("14 mar 2023");
  });

  it("mês abreviado sem ponto", () => {
    expect(displayMonthSlashYear("2023-03-14")).toBe("mar/2023");
    expect(displayShortMonthYear("2022-04-01")).toBe("abr/22");
    expect(displayMonthShort("2024-03-14")).toBe("mar");
  });

  it("mês por extenso, contando meses à frente e virando o ano", () => {
    expect(displayMonthName("2024-03-14")).toBe("março");
    expect(displayMonthName("2024-03-14", 1)).toBe("abril");
    expect(displayMonthName("2024-12-31", 1)).toBe("janeiro");
  });

  it("lista com vírgula e o último com “e”", () => {
    expect(displayList(["Ana", "Bia", "Lilo"])).toBe("Ana, Bia e Lilo");
    expect(displayList([])).toBe("");
  });
});

describe("displayQuantity", () => {
  it("tira os zeros à direita da string decimal", () => {
    expect(displayQuantity("10.00000000")).toBe("10");
    expect(displayQuantity("0.50000000")).toBe("0,5");
  });

  it("mantém as oito casas da cripto e agrupa o milhar", () => {
    expect(displayQuantity("0.00000001")).toBe("0,00000001");
    expect(displayQuantity("1500")).toBe("1.500");
  });
});
