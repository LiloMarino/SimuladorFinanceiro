import { describe, expect, it } from "vitest";
import type { SeriesCoverage } from "@/types";
import {
  activeShortcut,
  AXIS_MONTHS,
  axisPercent,
  axisPosition,
  bubbleLayout,
  buildShortcuts,
  dataEnds,
  dataFloor,
  displayDuration,
  endAtBoundary,
  parsePeriod,
  periodMonths,
  periodStop,
  shiftPeriod,
  startAtBoundary,
  timelineZones,
} from "./period";

const series = (key: string, start: string | null, real_end: string | null, generated_end: string | null = null) =>
  ({
    kind: "INDICATOR",
    key,
    name: key,
    start,
    real_end,
    generated_end,
    asset_class: null,
    segment: null,
  }) as SeriesCoverage;

const COVERAGE = [
  series("CDI", "1995-01-02", "2026-10-09", "2036-12-31"),
  series("SELIC", "1999-06-01", "2026-10-09", "2036-12-31"),
  series("IPCA", "2000-01-01", "2026-09-01", "2036-12-31"),
];
const FLOOR = { date: "2000-01-03", key: "CDI" };

describe("posição na linha", () => {
  it("o início conta desde o começo do dia e o fim até o limite dele", () => {
    expect(axisPosition("2020-04-01", "start")).toBe(327);
    expect(axisPosition("2026-10-31", "end")).toBe(406);
    expect(axisPercent(axisPosition("2040-12-31", "end"))).toBe(100);
  });

  it("prende aos limites do eixo", () => {
    expect(axisPercent(-5)).toBe(0);
    expect(axisPercent(AXIS_MONTHS + 5)).toBe(100);
  });
});

describe("duração", () => {
  it("conta os meses do início e do fim inclusive", () => {
    const period = parsePeriod("2020-04-01", "2026-10-31");
    expect(period && periodMonths(period)).toBe(79);
    expect(displayDuration(79)).toBe("6 anos e 7 meses");
  });

  it("usa o singular e omite a parte zerada", () => {
    expect(displayDuration(12)).toBe("1 ano");
    expect(displayDuration(13)).toBe("1 ano e 1 mês");
    expect(displayDuration(7)).toBe("7 meses");
    expect(displayDuration(60)).toBe("5 anos");
  });

  it("não existe período com data incompleta ou fim antes do início", () => {
    expect(parsePeriod("2020-04-01", "01/1")).toBeNull();
    expect(parsePeriod("2020-04-01", "2019-03-15")).toBeNull();
  });
});

describe("primeiro dia com dado", () => {
  it("é o início mais tardio entre os indicadores de taxa", () => {
    expect(dataFloor(COVERAGE)).toEqual({ date: "2000-01-01", key: "IPCA" });
  });

  it("o IPCA com início no meio do mês só vale no mês seguinte", () => {
    expect(dataFloor([series("IPCA", "2000-01-15", "2026-09-01")])).toEqual({ date: "2000-02-01", key: "IPCA" });
  });

  it("não olha ações nem indicadores fora da renda fixa", () => {
    const stock = { ...series("PETR4", "2012-12-03", "2026-10-09"), kind: "STOCK" } as SeriesCoverage;
    expect(dataFloor([...COVERAGE, stock, series("IBOV", "2010-01-04", "2026-10-09")])?.key).toBe("IPCA");
  });

  it("fica indefinido sem indicador com dado", () => {
    expect(dataFloor([])).toBeUndefined();
    expect(dataFloor([series("CDI", null, null)])).toBeUndefined();
  });

  it("não passa do começo da linha", () => {
    expect(dataFloor([series("CDI", "1980-01-02", "2026-10-09")])?.date).toBe("1993-01-01");
  });
});

describe("faixas da linha", () => {
  it("o fim do dado real e do futuro gerado é o mais cedo entre as séries", () => {
    expect(dataEnds(COVERAGE)).toEqual({ realEnd: "2026-09-01", generatedEnd: "2036-12-31" });
  });

  it("separa sem dado, real, futuro e o trecho que repete o último valor", () => {
    const zones = timelineZones(FLOOR, { realEnd: "2026-10-09", generatedEnd: "2036-12-31" });
    expect(zones.map((z) => z.kind)).toEqual(["no-data", "real", "future", "repeat"]);
    expect(zones[0]?.to).toBeCloseTo(14.59, 1);
    expect(zones[1]?.to).toBeCloseTo(70.37, 1);
    expect(zones[2]?.to).toBeCloseTo(91.67, 1);
    expect(zones[3]?.to).toBe(100);
  });

  it("sem futuro gerado a faixa violeta some", () => {
    const zones = timelineZones(FLOOR, { realEnd: "2026-10-09", generatedEnd: undefined });
    expect(zones.map((z) => z.kind)).toEqual(["no-data", "real", "repeat"]);
  });
});

describe("alças", () => {
  it("o início cai no dia 1 do mês", () => {
    expect(startAtBoundary(327, undefined)).toBe("2020-04-01");
  });

  it("o fim cai no último dia do mês", () => {
    expect(endAtBoundary(406)).toBe("2026-10-31");
    expect(endAtBoundary(AXIS_MONTHS)).toBe("2040-12-31");
  });

  it("o início para no primeiro dia com dado", () => {
    expect(startAtBoundary(10, FLOOR)).toBe("2000-01-03");
    expect(startAtBoundary(84, FLOOR)).toBe("2000-01-03");
    expect(startAtBoundary(85, FLOOR)).toBe("2000-02-01");
  });

  it("o fim não passa do fim da linha", () => {
    expect(endAtBoundary(AXIS_MONTHS + 40)).toBe("2040-12-31");
  });
});

describe("barra", () => {
  const origin = { start: "2020-04-01", end: "2026-10-31" };

  it("soma o mesmo deslocamento às duas pontas e mantém a duração em meses", () => {
    const moved = shiftPeriod(origin, -20, undefined);
    expect(moved).toEqual({ start: "2018-08-01", end: "2025-02-28" });
    expect(periodMonths(moved)).toBe(periodMonths(origin));
  });

  it("sem deslocamento devolve o período como está", () => {
    expect(shiftPeriod({ start: "2020-04-15", end: "2026-10-20" }, 0, undefined)).toEqual({
      start: "2020-04-15",
      end: "2026-10-20",
    });
  });

  it("para no primeiro dia com dado, mantendo a duração", () => {
    const moved = shiftPeriod({ start: "2000-06-01", end: "2006-12-31" }, -500, FLOOR);
    expect(moved).toEqual({ start: "2000-01-03", end: "2006-07-31" });
    expect(periodMonths(moved)).toBe(periodMonths({ start: "2000-06-01", end: "2006-12-31" }));
  });

  it("para no fim da linha, mantendo a duração", () => {
    const moved = shiftPeriod(origin, 9999, FLOOR);
    expect(moved.end).toBe("2040-12-31");
    expect(periodMonths(moved)).toBe(periodMonths(origin));
  });

  it("início antes do primeiro dia com dado não é puxado para a frente", () => {
    expect(shiftPeriod({ start: "1995-04-03", end: "2026-10-31" }, -3, FLOOR)).toEqual({
      start: "1995-04-03",
      end: "2026-10-31",
    });
  });
});

describe("parada nas bordas", () => {
  it("diz onde o período encosta", () => {
    expect(periodStop({ start: "2000-01-03", end: "2006-07-31" }, FLOOR)).toBe("floor");
    expect(periodStop({ start: "2034-06-01", end: "2040-12-31" }, FLOOR)).toBe("end");
    expect(periodStop({ start: "2020-04-01", end: "2026-10-31" }, FLOOR)).toBeNull();
  });
});

describe("atalhos", () => {
  const shortcuts = buildShortcuts("2026-10-23", FLOOR);
  const byId = (id: string) => shortcuts.find((s) => s.id === id);

  it("Até hoje termina hoje e Pra frente começa hoje", () => {
    expect(byId("past-5")?.period).toEqual({ start: "2021-10-23", end: "2026-10-23" });
    expect(byId("future-10")?.period).toEqual({ start: "2026-10-23", end: "2036-10-23" });
  });

  it("Tudo vai do primeiro dia com dado até hoje", () => {
    expect(byId("past-all")?.period).toEqual({ start: "2000-01-03", end: "2026-10-23" });
  });

  it("o atalho que começaria antes do primeiro dia com dado vem desligado, com o motivo", () => {
    expect(byId("past-20")?.blocked).toBeNull();
    const young = buildShortcuts("2026-10-23", { date: "2012-12-03", key: "PETR4" });
    expect(young.find((s) => s.id === "past-20")?.blocked).toBe("PETR4 só tem dado desde 03/12/2012");
    expect(young.find((s) => s.id === "past-10")?.blocked).toBeNull();
  });

  it("Pra frente desliga quando passa do fim da linha", () => {
    expect(buildShortcuts("2035-06-01", FLOOR).find((s) => s.id === "future-10")?.blocked).toMatch(/fim da linha/);
  });

  it("reconhece o atalho que o período reproduz", () => {
    expect(activeShortcut({ start: "2021-10-23", end: "2026-10-23" }, shortcuts)?.id).toBe("past-5");
    expect(activeShortcut({ start: "2021-10-01", end: "2026-10-23" }, shortcuts)).toBeUndefined();
  });
});

describe("datas sobre as alças", () => {
  it("separa as duas, cada uma para fora da sua alça, quando há espaço", () => {
    expect(bubbleLayout(56.77, 70.48)).toBe("split");
  });

  it("o fim vira para dentro quando não cabe à direita", () => {
    expect(bubbleLayout(50, 100)).toBe("split-flipped");
  });

  it("junta numa só quando o início encosta na borda ou as alças ficariam uma sobre a outra", () => {
    expect(bubbleLayout(14.59, 28.29)).toBe("merged-start");
    expect(bubbleLayout(86.28, 100)).toBe("merged-end");
  });
});
