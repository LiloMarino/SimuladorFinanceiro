import { describe, expect, it } from "vitest";
import {
  axisTicks,
  displaySignedThousands,
  displayThousands,
  goalOnScale,
  heldTypes,
  isPeriodAvailable,
  pointsInPeriod,
  pointsWithTypes,
  splitGainLoss,
  valueScale,
  type NetworthPoint,
} from "./networth-model";

const point = (date: string, networth = 0): NetworthPoint => ({
  date,
  networth,
  provided: 0,
  debt: 0,
  equity: 0,
  fixed: 0,
  cash: 0,
  equityByClass: undefined,
  goal: undefined,
});

describe("splitGainLoss", () => {
  it("fecha o trecho de ganho no ponto exato em que o patrimônio cruza o aportado", () => {
    // Aportado fixo em 100; o patrimônio vai de 110 a 90: a diferença passa de +10 a -10,
    // então o cruzamento está na metade do caminho (x = 5, valor 100)
    const { gains, losses } = splitGainLoss([
      { x: 0, provided: 100, networth: 110 },
      { x: 10, provided: 100, networth: 90 },
    ]);

    expect(gains).toEqual([
      [
        { x: 0, provided: 100, networth: 110 },
        { x: 5, provided: 100, networth: 100 },
      ],
    ]);
    expect(losses).toEqual([
      [
        { x: 5, provided: 100, networth: 100 },
        { x: 10, provided: 100, networth: 90 },
      ],
    ]);
  });

  it("mantém um trecho só enquanto o patrimônio fica do mesmo lado", () => {
    const { gains, losses } = splitGainLoss([
      { x: 0, provided: 100, networth: 100 },
      { x: 1, provided: 100, networth: 120 },
      { x: 2, provided: 100, networth: 130 },
    ]);

    expect(gains).toHaveLength(1);
    expect(gains[0]).toHaveLength(3);
    expect(losses).toEqual([]);
  });

  it("encostar na linha de aportado sem cruzar passa para o outro lado pelo ponto de contato", () => {
    const { gains, losses } = splitGainLoss([
      { x: 0, provided: 100, networth: 90 },
      { x: 1, provided: 100, networth: 100 },
      { x: 2, provided: 100, networth: 110 },
    ]);

    expect(losses).toEqual([
      [
        { x: 0, provided: 100, networth: 90 },
        { x: 1, provided: 100, networth: 100 },
      ],
    ]);
    expect(gains).toEqual([
      [
        { x: 1, provided: 100, networth: 100 },
        { x: 2, provided: 100, networth: 110 },
      ],
    ]);
  });
});

describe("períodos", () => {
  const daily = [point("2022-01-03"), point("2022-06-15"), point("2023-01-03")];

  it("um período só existe quando a partida já é tão longa quanto ele", () => {
    // Do primeiro ao último ponto passam 12 meses: 6M e 1A cabem
    expect(isPeriodAvailable(daily, "6M")).toBe(true);
    expect(isPeriodAvailable(daily, "1Y")).toBe(true);
    // 11 meses e 29 dias não completam 1A
    expect(isPeriodAvailable([point("2022-01-04"), point("2023-01-03")], "1Y")).toBe(false);
    expect(isPeriodAvailable([], "ALL")).toBe(true);
    expect(isPeriodAvailable([], "6M")).toBe(false);
  });

  it("a janela vai do dia equivalente, meses antes do último ponto, até o fim", () => {
    // 6 meses antes de 03/01/2023 é 03/07/2022: o ponto de junho fica de fora
    expect(pointsInPeriod(daily, "6M").map((p) => p.date)).toEqual(["2023-01-03"]);
    expect(pointsInPeriod(daily, "1Y").map((p) => p.date)).toEqual(["2022-01-03", "2022-06-15", "2023-01-03"]);
    expect(pointsInPeriod(daily, "ALL")).toBe(daily);
  });

  it("recuar meses limita o dia ao tamanho do mês de chegada", () => {
    // 31/03 menos 1 mês cai em fevereiro, que não tem 31: vale 28/02, não 03/03
    const points = [point("2023-02-28"), point("2023-03-31")];
    expect(pointsInPeriod(points, "6M")).toHaveLength(2);
  });
});

describe("valueScale", () => {
  it("desce abaixo do zero para caber a dívida e sobe até o maior valor", () => {
    // Dívida de 20 mil e pico de 123 mil: passos de 50 mil, de -50 a 150 mil
    const scale = valueScale([123_255, 95_000, -20_000]);
    expect(scale.ticks).toEqual([-50_000, 0, 50_000, 100_000, 150_000]);
    expect(scale.floor).toBe(-50_000);
    expect(scale.ceiling).toBe(150_000);
  });

  it("sem nenhum valor a escala é de 0 a 1", () => {
    expect(valueScale([0, 0])).toEqual({ ticks: [0, 1], floor: 0, ceiling: 1 });
  });
});

describe("goalOnScale", () => {
  const withGoal = (networth: number, goal: number | undefined): NetworthPoint => ({
    ...point("2022-01-03", networth),
    goal,
  });

  it("a meta só entra na escala quando o patrimônio chega a 10% dela", () => {
    // Meta de 100 mil: 7 mil são 7% (fora), 10 mil são 10% (dentro)
    expect(goalOnScale([withGoal(7_000, 100_000)])).toBe(false);
    expect(goalOnScale([withGoal(10_000, 100_000)])).toBe(true);
    expect(goalOnScale([withGoal(50_000, 100_000)])).toBe(true);
  });

  it("usa o maior patrimônio e a maior meta da janela", () => {
    // O pico de 12 mil passa de 10% da meta de 100 mil, mesmo que o último dia esteja em 5 mil
    expect(goalOnScale([withGoal(12_000, 100_000), withGoal(5_000, 100_000)])).toBe(true);
    // A meta reajustada para 150 mil faz os mesmos 12 mil valerem 8%
    expect(goalOnScale([withGoal(12_000, 100_000), withGoal(5_000, 150_000)])).toBe(false);
  });

  it("sem meta na janela não há o que deixar de fora", () => {
    expect(goalOnScale([withGoal(100, undefined)])).toBe(true);
  });
});

describe("axisTicks", () => {
  it("em janela de poucos dias rotula cada pregão em dd/MM", () => {
    const ticks = axisTicks(["2022-01-02", "2022-01-03", "2022-01-06"], 346);
    expect(ticks.map((t) => t.label)).toEqual(["02/01", "03/01", "06/01"]);
    expect(ticks.map((t) => t.anchor)).toEqual(["start", "middle", "end"]);
  });

  it("em janela longa rotula o início de alguns meses, a cada 12 quando o gráfico é estreito", () => {
    // Três anos de pregões em 300 px: só os janeiros cabem
    const dates: string[] = [];
    for (let year = 2020; year <= 2022; year++) {
      for (let month = 1; month <= 12; month++) {
        dates.push(`${year}-${String(month).padStart(2, "0")}-03`, `${year}-${String(month).padStart(2, "0")}-17`);
      }
    }
    const ticks = axisTicks(dates, 300);
    expect(ticks.map((t) => t.label)).toEqual(["jan/20", "jan/21", "jan/22"]);
    expect(ticks[0]?.anchor).toBe("start");
  });
});

describe("visão por tipo", () => {
  const split = (date: string, equityByClass: NetworthPoint["equityByClass"]) => ({ ...point(date), equityByClass });

  it("desenha só os dias em que a divisão por tipo foi gravada", () => {
    const points = [point("2020-01-02"), split("2020-01-03", {}), split("2020-01-06", { FII: 100 })];

    expect(pointsWithTypes(points).map((p) => p.date)).toEqual(["2020-01-03", "2020-01-06"]);
  });

  it("um tipo ganha painel quando esteve na carteira em algum dia, na ordem da renda variável", () => {
    const points = [
      split("2020-01-02", { CRYPTO: 50, STOCK: 0 }),
      split("2020-01-03", {}),
      split("2020-01-06", { FII: 100 }),
    ];

    expect(heldTypes(points)).toEqual(["FII", "CRYPTO"]);
  });
});

describe("formatação", () => {
  it("o eixo usa mil e mi, com sinal de menos tipográfico", () => {
    expect(displayThousands(0)).toBe("0");
    expect(displayThousands(50_000)).toBe("50 mil");
    expect(displayThousands(-50_000)).toBe("−50 mil");
    expect(displayThousands(1_500_000)).toBe("1,5 mi");
  });

  it("a variação do painel leva sinal e uma casa decimal", () => {
    expect(displaySignedThousands(19_040)).toBe("+19,0 mil");
    expect(displaySignedThousands(-1_000)).toBe("−1,0 mil");
    expect(displaySignedThousands(1_234_000)).toBe("+1,2 mi");
  });
});
