import { describe, expect, it } from "vitest";
import type { TimelinePoint } from "@/types";
import { placeTrend, runoffStart, trendParties, trendSummary, trendTick } from "./map-trend";

function poll(date: string, kind: TimelinePoint["kind"], entries: Record<number, number>): TimelinePoint {
  return {
    date,
    kind,
    happened: true,
    leaders: [],
    result: null,
    poll: {
      date,
      previous_date: null,
      next_date: null,
      runoff: kind === "RUNOFF_POLL",
      places: [
        {
          code: "BA",
          undecided: "10",
          previous_entries: [],
          entries: Object.entries(entries).map(([id, points]) => ({ party_id: Number(id), points: String(points) })),
        },
      ],
    },
  };
}

function result(date: string, kind: TimelinePoint["kind"], entries: Record<number, number>): TimelinePoint {
  return {
    date,
    kind,
    happened: true,
    leaders: [],
    poll: null,
    result: {
      round: kind === "RUNOFF" ? 2 : 1,
      previous_date: null,
      date,
      national: [],
      places: [
        {
          code: "BA",
          previous_entries: [],
          entries: Object.entries(entries).map(([id, points]) => ({
            party_id: Number(id),
            points: String(points),
            share: "0",
          })),
        },
      ],
    },
  };
}

const points = [
  poll("2030-01-01", "POLL", { 1: 37, 2: 30 }),
  poll("2030-02-01", "POLL", { 1: 45, 2: 30 }),
  result("2030-10-06", "FIRST_ROUND", { 1: 30, 2: 30, 3: 40 }),
  poll("2030-10-13", "RUNOFF_POLL", { 1: 59, 2: 31 }),
  { ...poll("2030-10-27", "RUNOFF", {}), happened: false },
];

describe("placeTrend", () => {
  const rows = placeTrend(points, "BA");

  it("usa os pontos na pesquisa e a fatia dos votos válidos na apuração", () => {
    expect(rows[0]?.values[1]).toBe(37);
    expect(rows[0]?.undecided).toBe(10);
    expect(rows[2]?.values[3]).toBe(40);
    expect(rows[2]?.undecided).toBeNull();
  });

  it("deixa de fora o ponto que não aconteceu e o partido eliminado", () => {
    expect(rows).toHaveLength(4);
    expect(rows[3]?.values[3]).toBeUndefined();
    expect(trendParties(rows)).toEqual([1, 2, 3]);
  });

  it("acha o começo do 2º turno e rotula só o começo e os turnos", () => {
    expect(runoffStart(rows)).toBe(3);
    expect(rows.map((_, index) => trendTick(rows, index))).toEqual(["jan", "", "1º t.", ""]);
  });
});

describe("trendSummary", () => {
  it("resume o partido do começo ao 2º turno", () => {
    const rows = placeTrend(points, "BA");
    expect(trendSummary(rows, 1, "PTD", "Bahia")).toBe(
      "Bahia: o PTD foi de 37% em jan a 45% em fev, teve 30% no 1º turno e no 2º turno tem 59%.",
    );
  });

  it("sem pesquisa mensal do partido não há frase", () => {
    expect(trendSummary(placeTrend(points, "BA"), 9, "XX", "Bahia")).toBeNull();
  });
});
