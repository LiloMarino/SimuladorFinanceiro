import { describe, expect, it } from "vitest";
import type { SeriesCoverage } from "@/types";
import { afterEnd } from "./after-end";

const series = (patch: Partial<SeriesCoverage>): SeriesCoverage => ({
  kind: "INDICATOR",
  key: "CDI",
  name: "CDI",
  start: "1986-03-06",
  real_end: "2026-11-09",
  generated_end: null,
  corrected_days: 0,
  has_generated_future: true,
  asset_class: null,
  origin: null,
  segment: null,
  ...patch,
});

describe("afterEnd", () => {
  it("repete o último valor enquanto a série ganha futuro e ainda não tem", () => {
    expect(afterEnd(series({}))).toBe("repeat");
  });

  it("usa o futuro gerado quando ele existe", () => {
    expect(afterEnd(series({ generated_end: "2045-12-31" }))).toBe("generated");
  });

  it("a série da economia sem futuro gerado é calculada na partida", () => {
    expect(afterEnd(series({ kind: "MACRO", key: "GDP_GROWTH", has_generated_future: false }))).toBe("computed");
  });

  it("o Fed Funds está na economia, mas ganha futuro gerado", () => {
    expect(afterEnd(series({ kind: "MACRO", key: "FED_FUNDS", generated_end: "2045-12-31" }))).toBe("generated");
  });

  it("o Focus termina na última pesquisa", () => {
    expect(afterEnd(series({ kind: "EXPECTATION", key: "FOCUS_SELIC", has_generated_future: false }))).toBe("none");
  });
});
