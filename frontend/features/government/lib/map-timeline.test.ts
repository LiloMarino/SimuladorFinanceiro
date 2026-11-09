import { describe, expect, it } from "vitest";
import type { TimelineMilestone, TimelinePoint, TimelineYear } from "@/types";
import {
  RULER_MARGIN,
  finalists,
  flagText,
  lastHappened,
  markerDelta,
  milestoneCount,
  milestoneSlots,
  pointAt,
  pointLabel,
  rulerLayout,
  visibleYears,
} from "./map-timeline";

function point(date: string, kind: TimelinePoint["kind"], happened = true, poll: TimelinePoint["poll"] = null) {
  return { date, kind, happened, leaders: [], poll, result: null } satisfies TimelinePoint;
}

function milestone(
  kind: TimelineMilestone["kind"],
  partyId: number,
  after = "2030-03-01",
  itemCount = 1,
): TimelineMilestone {
  return {
    after,
    before: "2030-04-01",
    party_id: partyId,
    kind,
    region: null,
    items: Array.from({ length: itemCount }, () => ({
      day: after,
      action: null,
      group: null,
      rival_id: null,
      partner_id: null,
      title: null,
    })),
  };
}

function year(value: number): TimelineYear {
  return { year: value, cycle: value, status: "DONE", opens_on: `${value}-01-01`, winner: null };
}

function pollOf(date: string, rows: Record<string, Record<number, number>>): NonNullable<TimelinePoint["poll"]> {
  return {
    date,
    previous_date: null,
    next_date: null,
    runoff: false,
    places: Object.entries(rows).map(([code, entries]) => ({
      code,
      undecided: "0",
      previous_entries: [],
      entries: Object.entries(entries).map(([party, points]) => ({ party_id: Number(party), points: String(points) })),
    })),
  };
}

describe("rulerLayout", () => {
  it("espaça os pontos por igual e cobre a largura menos a folga dos dois lados", () => {
    const points = [point("a", "POLL"), point("b", "POLL"), point("c", "FIRST_ROUND")];
    const { xs, step } = rulerLayout(points, 126);
    expect(step).toBe(37);
    expect(xs).toEqual([RULER_MARGIN, RULER_MARGIN + 37, RULER_MARGIN + 74]);
  });

  it("dá 1,5 passo do 1º turno à primeira semanal", () => {
    const points = [point("a", "POLL"), point("b", "FIRST_ROUND"), point("c", "RUNOFF_POLL"), point("d", "RUNOFF")];
    const { xs, step } = rulerLayout(points, 2 * RULER_MARGIN + 350);
    expect(step).toBe(100);
    expect(xs[2]! - xs[1]!).toBe(150);
    expect(xs[3]! - xs[2]!).toBe(100);
  });

  it("com um ponto só, ele fica na folga da esquerda", () => {
    expect(rulerLayout([point("a", "POLL")], 500).xs).toEqual([RULER_MARGIN]);
  });
});

describe("milestoneSlots", () => {
  it("promessas e ações são só do partido em foco; alianças aparecem sempre", () => {
    const slots = milestoneSlots([milestone("PROMISE", 1), milestone("CAMPAIGN", 2), milestone("ALLIANCE", 2)], 1);
    expect(slots).toHaveLength(1);
    expect(slots[0]!.all.map((m) => m.kind)).toEqual(["PROMISE", "ALLIANCE"]);
  });

  it("mostra no máximo 2 marcos por intervalo e deixa o resto em hidden", () => {
    const [slot] = milestoneSlots([milestone("PROMISE", 1), milestone("CAMPAIGN", 1), milestone("ALLIANCE", 1)], 1);
    expect(slot!.shown.map((m) => m.kind)).toEqual(["PROMISE", "CAMPAIGN"]);
    expect(slot!.hidden.map((m) => m.kind)).toEqual(["ALLIANCE"]);
    expect(slot!.all).toHaveLength(3);
  });

  it("separa por intervalo e ordena pela data", () => {
    const slots = milestoneSlots([milestone("PROMISE", 1, "2030-05-01"), milestone("PROMISE", 1, "2030-03-01")], 1);
    expect(slots.map((slot) => slot.after)).toEqual(["2030-03-01", "2030-05-01"]);
  });

  it("sem partido em foco, só as alianças", () => {
    const slots = milestoneSlots([milestone("PROMISE", 1), milestone("ALLIANCE", 1)], null);
    expect(slots[0]!.all.map((m) => m.kind)).toEqual(["ALLIANCE"]);
  });
});

describe("milestoneCount", () => {
  it("o selo mostra o número de itens, e some com um só", () => {
    expect(milestoneCount(milestone("CAMPAIGN", 1, "2030-03-01", 1))).toBeNull();
    expect(milestoneCount(milestone("CAMPAIGN", 1, "2030-03-01", 3))).toBe(3);
    expect(milestoneCount(milestone("CAMPAIGN", 1, "2030-03-01", 11))).toBe(11);
  });
});

describe("visibleYears", () => {
  it("até 4 eleições todas ficam no seletor", () => {
    const years = [2018, 2022, 2026, 2030].map(year);
    expect(visibleYears(years)).toEqual({ row: years, older: [] });
  });

  it("com 5 ou mais ficam as 3 mais recentes e o resto vai para o Anteriores", () => {
    const years = [2014, 2018, 2022, 2026, 2030].map(year);
    const { row, older } = visibleYears(years);
    expect(row.map((item) => item.year)).toEqual([2022, 2026, 2030]);
    expect(older.map((item) => item.year)).toEqual([2014, 2018]);
  });
});

describe("pointLabel", () => {
  it("mês nas mensais, dia e mês nas semanais, nome nos turnos", () => {
    expect(pointLabel({ kind: "POLL", date: "2030-04-01" })).toBe("abr");
    expect(pointLabel({ kind: "RUNOFF_POLL", date: "2030-10-07" })).toBe("07 out");
    expect(pointLabel({ kind: "FIRST_ROUND", date: "2030-10-06" })).toBe("1º turno");
    expect(pointLabel({ kind: "RUNOFF", date: "2030-10-27" })).toBe("2º turno");
  });
});

describe("lastHappened e pointAt", () => {
  const points = [point("2030-01-01", "POLL"), point("2030-02-01", "POLL"), point("2030-03-01", "POLL", false)];

  it("o hoje é o último ponto que já aconteceu", () => {
    expect(lastHappened(points)?.date).toBe("2030-02-01");
  });

  it("a data da URL vale quando o ponto existe e já aconteceu", () => {
    expect(pointAt(points, "2030-01-01")?.date).toBe("2030-01-01");
  });

  it("data ausente, desconhecida ou futura cai no hoje", () => {
    expect(pointAt(points, null)?.date).toBe("2030-02-01");
    expect(pointAt(points, "2031-01-01")?.date).toBe("2030-02-01");
    expect(pointAt(points, "2030-03-01")?.date).toBe("2030-02-01");
  });
});

describe("markerDelta", () => {
  const regions = [
    { code: "NE", electorate_share: "0.25" },
    { code: "SE", electorate_share: "0.75" },
  ];
  const before = point("a", "POLL", true, pollOf("a", { NE: { 1: 20 }, SE: { 1: 40 } }));
  const after = point("b", "POLL", true, pollOf("b", { NE: { 1: 25 }, SE: { 1: 42 } }));

  it("pesa as regiões pelo eleitorado no país e dá a variação da região do marco", () => {
    // país: 0,25×25 + 0,75×42 = 37,75 contra 0,25×20 + 0,75×40 = 35 → +2,75
    expect(markerDelta(before, after, 1, "NE", regions)).toEqual({ national: 3, region: { code: "NE", delta: 5 } });
  });

  it("sem região no marco, só o país", () => {
    expect(markerDelta(before, after, 1, null, regions)?.region).toBeNull();
  });

  it("sem pesquisa do partido num dos pontos, nada", () => {
    expect(markerDelta(point("c", "POLL"), after, 1, null, regions)).toBeNull();
    expect(markerDelta(before, after, 9, null, regions)).toBeNull();
  });
});

describe("finalists", () => {
  const first = {
    ...point("2030-10-06", "FIRST_ROUND"),
    result: {
      round: 1,
      previous_date: null,
      date: "2030-10-06",
      places: [],
      national: [
        { party_id: 3, share: "0.2", points: "20" },
        { party_id: 1, share: "0.45", points: "45" },
        { party_id: 2, share: "0.35", points: "35" },
      ],
    },
  } satisfies TimelinePoint;

  it("devolve os dois mais votados quando há 2º turno", () => {
    expect(finalists([first, point("2030-10-13", "RUNOFF_POLL")])).toEqual([1, 2]);
  });

  it("fica vazio quando a eleição acabou no 1º turno", () => {
    expect(finalists([first])).toEqual([]);
  });
});

describe("flagText", () => {
  const parties = [{ id: 1, abbr: "PTD" }];
  const first = {
    ...point("2030-10-06", "FIRST_ROUND"),
    result: {
      round: 1,
      previous_date: null,
      date: "2030-10-06",
      places: [],
      national: [{ party_id: 1, share: "52", points: "40" }],
    },
  } satisfies TimelinePoint;

  it("escreve só a data numa pesquisa", () => {
    expect(flagText(point("2030-03-01", "POLL"), [], parties, false)).toBe("01 mar 2030");
  });

  it("diz quem venceu quando o 1º turno decidiu", () => {
    expect(flagText(first, [first], parties, false)).toBe("1º turno · 06 out 2030 · PTD venceu com 52%");
  });

  it("não diz o vencedor quando há 2º turno", () => {
    expect(flagText(first, [first, point("2030-10-13", "RUNOFF_POLL")], parties, false)).toBe("1º turno · 06 out 2030");
  });

  it("avisa que o resultado vale até a próxima eleição no mandato", () => {
    expect(flagText(point("2030-10-27", "RUNOFF"), [], parties, true)).toBe(
      "2º turno · 27 out 2030 · vale até a próxima eleição",
    );
  });
});
