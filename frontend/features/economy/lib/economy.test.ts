import { describe, expect, it } from "vitest";
import type { EconomyEffect, EconomyPanel } from "@/types";
import {
  copomLabel,
  economyRows,
  effectShares,
  inflationBreakdown,
  stocksEffect,
  sumEffects,
  growthLines,
  ipcaExample,
  lastCopomNote,
  lastMonthChange,
  monthChangeNote,
  selicExample,
  signedPoints,
  targetNote,
  unemploymentExample,
} from "./economy";

const point = (date: string, selic: string, ipca: string, target = "0.035", growth = "0.02") => ({
  tolerance: "0.015",
  growth,
  unemployment: "0.09",
  debt: null,
  premium: null,
  ibovespa: null,
  stored_selic: null,
  stored_ipca: null,
  stored_ibovespa: null,
  date,
  selic,
  ipca,
  real_rate: String(Number(selic) - Number(ipca)),
  target,
});

const growthParts: EconomyPanel["growth_parts"] = {
  trend: "0.02",
  real_rate: "0.0045",
  real_rate_part: "0.01825",
  neutral_real_rate: "0.05",
  stocks: "-0.17",
  stocks_part: "-0.011",
  target: "0.02",
  growth: "0.022",
};

const rise = { date: "2022-03-16", change: "0.0075", selic: "0.1075" };

describe("economyRows", () => {
  it("liga a mudança do Copom ao ponto do mesmo dia", () => {
    const panel: EconomyPanel = {
      points: [point("2022-02-28", "0.1", "0.05"), point("2022-03-16", "0.1075", "0.06")],
      copom_changes: [rise],
      growth_parts: growthParts,
      debt: null,
      effects: null,
    };
    const [first, second] = economyRows(panel);
    expect(first?.copom).toBeUndefined();
    expect(second?.copom).toEqual(rise);
    // 10,75% de SELIC com 6% de IPCA
    expect(second?.realRate).toBeCloseTo(0.0475, 6);
  });
});

describe("copomLabel", () => {
  it("diz o tamanho e o novo nível quando sobe", () => {
    expect(copomLabel(rise)).toBe("Copom subiu a SELIC em 0,75 p.p., para 10,75%");
  });

  it("diz baixou quando a mudança é negativa", () => {
    expect(copomLabel({ date: "2022-05-04", change: "-0.005", selic: "0.1025" })).toBe(
      "Copom baixou a SELIC em 0,50 p.p., para 10,25%",
    );
  });
});

describe("economyRows", () => {
  const panel: EconomyPanel = {
    points: [
      point("2021-01-29", "0.02", "0.03"),
      point("2022-03-16", "0.1075", "0.06"),
      point("2022-04-29", "0.11", "0.06"),
    ],
    copom_changes: [],
    growth_parts: growthParts,
    debt: null,
    effects: null,
  };

  it("monta a faixa da meta com a tolerância para os dois lados", () => {
    const [first] = economyRows(panel);
    // meta de 3,5% ± 1,5 ponto: de 2% a 5%
    expect(first?.band[0]).toBeCloseTo(0.02, 6);
    expect(first?.band[1]).toBeCloseTo(0.05, 6);
  });

  it("no recorte de 12 meses deixa só os pontos do último ano", () => {
    expect(economyRows(panel, "year").map((row) => row.selic)).toEqual([0.1075, 0.11]);
  });
});

describe("lastCopomNote", () => {
  it("avisa quando a SELIC ainda não mudou", () => {
    expect(lastCopomNote([])).toBe("Sem mudança do Copom ainda");
  });

  it("mostra o sentido, o tamanho e o mês da última mudança", () => {
    expect(lastCopomNote([rise])).toBe("▲ 0,75 p.p. em mar/22");
  });
});

describe("exemplos em reais", () => {
  it("a SELIC de 10,75% rende R$ 10,75 em R$ 100", () => {
    const text = selicExample(point("2022-03-16", "0.1075", "0.06"));
    expect(text).toContain("110,75");
  });

  it("o IPCA de 6% faz R$ 100 custarem R$ 106", () => {
    expect(ipcaExample(point("2022-03-16", "0.1075", "0.06"))).toContain("106,00");
  });
});

describe("targetNote", () => {
  it("diz a meta do ano", () => {
    expect(targetNote(point("2022-03-16", "0.1", "0.06"))).toBe("meta de 3,50%");
  });
});

describe("lastMonthChange", () => {
  it("é a diferença do último fechamento, mesmo com pontos repetidos do Copom no meio do mês", () => {
    const points = [
      point("2022-01-31", "0.1", "0.05", "0.035", "0.020"),
      point("2022-02-28", "0.1", "0.05", "0.035", "0.023"),
      point("2022-03-10", "0.11", "0.05", "0.035", "0.023"),
    ];

    expect(lastMonthChange(points, "growth")).toBeCloseTo(0.003, 6);
  });

  it("sem nenhum fechamento ainda devolve nulo", () => {
    expect(lastMonthChange([point("2022-01-03", "0.1", "0.05")], "growth")).toBeNull();
  });
});

describe("monthChangeNote", () => {
  it("diz o sentido e o tamanho em pontos", () => {
    expect(monthChangeNote(-0.003)).toBe("▼ 0,3 no mês");
    expect(monthChangeNote(0.012)).toBe("▲ 1,2 no mês");
  });

  it("variação menor que meia casa conta como estável", () => {
    expect(monthChangeNote(0.0002)).toBe("estável no mês");
  });
});

describe("signedPoints", () => {
  it("usa o menos tipográfico e uma casa", () => {
    expect(signedPoints(0.02)).toBe("+2,0");
    expect(signedPoints(-0.009)).toBe("−0,9");
  });
});

describe("growthLines", () => {
  it("explica as três partes do alvo, cada uma com o motivo", () => {
    const [trend, realRate, stocks] = growthLines(growthParts);

    expect(trend?.value).toBe("+2,0");
    expect(realRate?.label).toBe("Juro real abaixo do neutro");
    expect(realRate?.detail).toBe("0,45% contra 5%: crédito barato empurra");
    expect(stocks?.detail).toBe("Ibovespa −17%: empresas investem menos");
    expect(stocks?.tone).toBe("down");
  });

  it("com juro real acima do neutro o crédito caro freia", () => {
    const [, realRate] = growthLines({ ...growthParts, real_rate: "0.08", real_rate_part: "-0.012" });

    expect(realRate?.label).toBe("Juro real acima do neutro");
    expect(realRate?.detail).toContain("crédito caro freia");
  });
});

describe("unemploymentExample", () => {
  it("lê o desemprego em 'de cada 100'", () => {
    expect(unemploymentExample({ ...point("2022-03-16", "0.1", "0.05"), unemployment: "0.116" })).toBe(
      "De cada 100 pessoas que procuram emprego, 11,6 não acham.",
    );
  });
});

const effect = (kind: EconomyEffect["kind"], inflation: string, curve: string[] = []): EconomyEffect => ({
  measure_id: 1,
  kind,
  title: "Auxílio: de 0,9% para 1,4% do PIB",
  value: "0.014",
  before: "0.009",
  effective: "2020-01-10",
  peak_on: "2020-07-10",
  faded_on: "2021-08-10",
  phase: "RISING",
  inflation,
  selic: String(Number(inflation) * 1.5),
  stocks: "-0.02",
  curve,
  elapsed_months: 2,
});

describe("efeitos das medidas", () => {
  const effects = [
    effect("WELFARE_SPENDING", "0.55"),
    effect("PUBLIC_WORKS", "0.2"),
    effect("SERVANT_RAISE", "-0.1"),
    effect("WELFARE_SPENDING", "0.25"),
  ];

  it("soma os pontos de IPCA e de SELIC", () => {
    expect(sumEffects(effects, "inflation")).toBeCloseTo(0.9, 6);
    expect(sumEffects(effects, "selic")).toBeCloseTo(1.35, 6);
  });

  it("agrupa por tipo de medida, do que mais soma ao que tira", () => {
    expect(inflationBreakdown(effects).map((part) => [part.label, Math.round(part.points * 100) / 100])).toEqual([
      ["Auxílio", 0.8],
      ["Obras", 0.2],
      ["Reajuste dos servidores", -0.1],
    ]);
  });

  it("lê a curva no mês que já correu desde a vigência", () => {
    const withCurve = [effect("WELFARE_SPENDING", "0.5", ["0", "0.1", "0.2", "0.3"])];
    // 2 meses e meio depois de 10 jan: mês 2 da curva
    const shares = effectShares(withCurve, new Date(2020, 2, 25).getTime());
    expect(shares).toEqual([{ kind: "WELFARE_SPENDING", label: "Auxílio", points: 0.2 }]);
    expect(effectShares(withCurve, new Date(2019, 11, 1).getTime())).toEqual([]);
  });

  it("compara o Ibovespa da partida com o da história", () => {
    const today = { ...point("2020-04-14", "0.05", "0.03"), ibovespa: "75700", stored_ibovespa: "78800" };
    expect(stocksEffect(today)).toBeCloseTo(-0.0393, 3);
    expect(stocksEffect(point("2020-04-14", "0.05", "0.03"))).toBeNull();
  });
});
