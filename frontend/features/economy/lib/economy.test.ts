import { describe, expect, it } from "vitest";
import type { EconomyEffect, EconomyLinkEffect, EconomyPanel } from "@/types";
import {
  activeLinks,
  copomLabel,
  dollarLines,
  dollarNote,
  economyRows,
  effectShares,
  governmentShift,
  inflationBreakdown,
  selicByGovernment,
  stocksEffect,
  sumEffects,
  growthLines,
  ipcaExample,
  lastCopomNote,
  lastMonthChange,
  monthTicks,
  monthChangeNote,
  selicExample,
  stabilizingNote,
  targetNote,
  unemploymentExample,
} from "./economy";
import { signedPoints } from "./economy-metrics";

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
  dollar: "5",
  stored_dollar: null,
  date,
  selic,
  ipca,
  real_rate: String(Number(selic) - Number(ipca)),
  target,
});

const dollarParts: EconomyPanel["dollar_parts"] = {
  history: "5",
  premium: "0.4",
  real_rate: "-0.1",
  total: "5.3",
  inflation: "0.35",
};

const growthParts: EconomyPanel["growth_parts"] = {
  history_growth: "0.02",
  real_rate: "-0.004",
  stocks: "0.003",
  works: "0",
  impulse: "0.005",
  inflation: "-0.008",
  crowding_out: "0",
  growth: "0.016",
  history_unemployment: "0.09",
  unemployment: "0.088",
};

const rise = { date: "2022-03-16", change: "0.0075", selic: "0.1075" };

describe("economyRows", () => {
  it("liga a mudança do Copom ao ponto do mesmo dia", () => {
    const panel: EconomyPanel = {
      points: [point("2022-02-28", "0.1", "0.05"), point("2022-03-16", "0.1075", "0.06")],
      copom_changes: [rise],
      growth_parts: growthParts,
      dollar_parts: dollarParts,
      debt: null,
      effects: null,
      links: null,
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
    dollar_parts: dollarParts,
    debt: null,
    effects: null,
    links: null,
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
  it("abre o que a partida somou à história em seis parcelas, cada uma com o motivo", () => {
    const [realRate, stocks, works, impulse, inflation, crowding] = growthLines(growthParts);

    expect(realRate?.value).toBe("−0,4");
    expect(realRate?.tone).toBe("down");
    expect(realRate?.detail).toContain("crédito mais caro freia");
    expect(stocks?.detail).toContain("empresas investem mais");
    expect(works?.tone).toBe("neutral");
    expect(impulse?.value).toBe("+0,5");
    expect(impulse?.metric?.label).toBe("Impulso fiscal");
    expect(inflation?.value).toBe("−0,8");
    expect(inflation?.tone).toBe("down");
    expect(inflation?.detail).toContain("acima de 12%");
    expect(crowding?.tone).toBe("neutral");
    expect(crowding?.metric?.label).toBe("Crédito encarecido");
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

const link = (kind: EconomyLinkEffect["link"], inflation: string, stocks = "0", growth = "0"): EconomyLinkEffect => ({
  link: kind,
  gap: "0.02",
  inflation,
  selic: String(Number(inflation) * 1.5),
  stocks,
  growth,
  unemployment: "0",
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

  it("põe as ligações que mexem na inflação junto das medidas, pelo nome da ligação", () => {
    const links = [link("DOLLAR", "0.4"), link("PHILLIPS", "-0.2"), link("GDP", "0", "0.03")];
    expect(inflationBreakdown(effects, links).map((part) => [part.label, Math.round(part.points * 100) / 100])).toEqual(
      [
        ["Auxílio", 0.8],
        ["Câmbio", 0.4],
        ["Obras", 0.2],
        ["Reajuste dos servidores", -0.1],
        ["Desemprego baixo", -0.2],
      ],
    );
  });

  it("guarda só as ligações que mexem em algo hoje", () => {
    const links = [link("FISCAL_RISK", "0.004", "0.0001"), link("PHILLIPS", "0.2"), link("GDP", "0", "0.03")];
    expect(activeLinks(links).map((item) => item.link)).toEqual(["PHILLIPS", "GDP"]);
  });

  it("guarda a ligação que só mexe no crescimento", () => {
    const links = [link("CROWDING_OUT", "0", "0", "-0.012"), link("INFLATION_BRAKE", "0", "0", "0.0001")];
    expect(activeLinks(links).map((item) => item.link)).toEqual(["CROWDING_OUT"]);
  });

  it("vê a SELIC do governo pela ligação que só existe com ela", () => {
    expect(selicByGovernment([link("PHILLIPS", "0.2")])).toBe(false);
    expect(selicByGovernment([link("SELIC", "0", "-0.02"), link("REAL_RATE", "0.1")])).toBe(true);
  });

  it("mede o que o governo soma a uma série em pontos, contra a história", () => {
    expect(governmentShift("0.115", "0.1")).toBeCloseTo(1.5, 6);
    expect(governmentShift("0.115", null)).toBeNull();
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

describe("stabilizingNote", () => {
  it("diz quanto falta quando o primário está abaixo do que estabiliza", () => {
    expect(stabilizingNote(0.01, 0.0296)).toBe("Faltam 2,0 pontos do PIB de primário para a dívida parar de subir.");
  });

  it("diz quanto sobra quando o primário passa do que estabiliza", () => {
    expect(stabilizingNote(0.03, 0.0184)).toBe("Sobram 1,2 ponto do PIB de primário: a dívida cai.");
  });

  it("conta o déficit que a dívida aguenta como primário a menos", () => {
    expect(stabilizingNote(-0.02, -0.005)).toBe("Faltam 1,5 ponto do PIB de primário para a dívida parar de subir.");
  });

  it("reconhece o primário que já segura a dívida", () => {
    expect(stabilizingNote(0.02, 0.02)).toBe("O primário segura a dívida onde está.");
  });
});

describe("dólar da partida", () => {
  it("abre o dólar em parcelas do prêmio e do juro real, com o sinal e o tom de cada uma", () => {
    const [premium, realRate] = dollarLines(dollarParts);
    // R$ 0,40 de prêmio a mais encarece o dólar; R$ 0,10 de juro real a mais o barateia
    expect([premium?.label, premium?.value, premium?.tone]).toEqual(["Prêmio de risco", "+R$ 0,40", "up"]);
    expect([realRate?.label, realRate?.value, realRate?.tone]).toEqual(["Juro real", "−R$ 0,10", "down"]);
  });

  it("trata a parcela abaixo de meio centavo como sem efeito", () => {
    const [premium] = dollarLines({ ...dollarParts, premium: "0.004" });
    expect(premium?.tone).toBe("neutral");
  });

  it("compara o dólar com o da história em %", () => {
    // R$ 5,50 contra R$ 5,00: 10% acima
    expect(dollarNote({ ...point("2022-03-16", "0.1", "0.05"), dollar: "5.5", stored_dollar: "5" })).toBe(
      "+10,0% pelo governo",
    );
    expect(dollarNote({ ...point("2022-03-16", "0.1", "0.05"), dollar: "5", stored_dollar: "5" })).toBe(
      "sem efeito do governo",
    );
    expect(dollarNote(point("2022-03-16", "0.1", "0.05"))).toBe("a PTAX, em reais");
  });

  it("leva o dólar de cada ponto para a linha do gráfico", () => {
    const panel: EconomyPanel = {
      points: [point("2022-02-28", "0.1", "0.05"), point("2022-03-16", "0.1", "0.05")],
      copom_changes: [],
      growth_parts: growthParts,
      dollar_parts: dollarParts,
      debt: null,
      effects: null,
      links: null,
    };
    expect(economyRows(panel).map((row) => row.dollar)).toEqual([5, 5]);
  });
});

describe("monthTicks", () => {
  const day = (iso: string) => new Date(`${iso}T00:00:00`).getTime();

  it("marca o início de cada mês do intervalo, sem repetir mês", () => {
    const ticks = monthTicks([day("2021-12-15"), day("2022-03-10")]);
    expect(ticks).toEqual([day("2022-01-01"), day("2022-02-01"), day("2022-03-01")]);
  });

  it("espaça as marcas quando o intervalo passa do máximo", () => {
    // 24 inícios de mês em no máximo 6 marcas: de 4 em 4 meses
    const ticks = monthTicks([day("2020-01-01"), day("2021-12-31")], 6);
    expect(ticks).toHaveLength(6);
    expect(ticks[0]).toBe(day("2020-01-01"));
    expect(ticks[1]).toBe(day("2020-05-01"));
  });

  it("sem linhas ou sem virada de mês não há marca", () => {
    expect(monthTicks([])).toEqual([]);
    expect(monthTicks([day("2022-01-05"), day("2022-01-20")])).toEqual([]);
  });
});
