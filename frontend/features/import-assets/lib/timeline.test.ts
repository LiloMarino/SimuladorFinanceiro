import { describe, expect, it } from "vitest";
import type { SeriesCoverage } from "@/types";
import { timelineOffset, timelineRange, timelineTicks, timelineTodayOffset } from "./timeline";

const series = (start: string, real_end: string, generated_end: string | null = null): SeriesCoverage => ({
  kind: "INDICATOR",
  key: "X",
  name: "X",
  start,
  real_end,
  generated_end,
  corrected_days: 0,
  has_generated_future: true,
  asset_class: null,
  origin: null,
  segment: null,
});

// Hoje = 12/11/2026: o eixo vai de 01/01/1980 até 12/11/2046
const TODAY = new Date(2026, 10, 12);
const range = timelineRange([series("1980-01-01", "2026-09-01"), series("1986-03-06", "2026-11-09")], TODAY);

describe("timelineRange", () => {
  it("vai do início mais antigo até 20 anos depois de hoje", () => {
    expect(range.start).toBe(new Date(1980, 0, 1).getTime());
    expect(range.end).toBe(new Date(2046, 10, 12).getTime());
    expect(range.today).toBe(TODAY.getTime());
  });

  it("estica o fim quando um futuro gerado passa de hoje + 20 anos", () => {
    const wide = timelineRange([series("1980-01-01", "2026-09-01", "2050-12-31")], TODAY);
    expect(wide.end).toBe(new Date(2050, 11, 31).getTime());
  });

  it("sem dado nenhum, o eixo começa em hoje", () => {
    expect(timelineRange([], TODAY).start).toBe(TODAY.getTime());
  });
});

describe("timelineOffset", () => {
  it("põe o início do eixo em 0% e o fim em 100%", () => {
    expect(timelineOffset("1980-01-01", range)).toBe(0);
    expect(timelineOffset("2046-11-12", range)).toBeCloseTo(100, 6);
  });

  it("hoje fica na posição real: 1980 → 2026 são 46,86 dos 66,86 anos, uns 70%", () => {
    expect(timelineTodayOffset(range)).toBeCloseTo(70.1, 0);
  });
});

describe("timelineTicks", () => {
  it("mostra o ano inicial, os anos redondos que cabem, hoje e o ano final", () => {
    // 2020 encostaria em "hoje" e 2040 no ano final: ficam só 1980, 2000, hoje e 2046
    expect(timelineTicks(range).map((tick) => tick.label)).toEqual(["1980", "2000", "hoje", "2046"]);
  });

  it("alinha o ano inicial à esquerda e o final à direita", () => {
    const ticks = timelineTicks(range);
    expect(ticks[0]).toMatchObject({ position: 0, align: "start" });
    expect(ticks[ticks.length - 1]).toMatchObject({ position: 100, align: "end" });
  });
});
