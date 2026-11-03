import { describe, expect, it } from "vitest";
import { archiveMonths, monthOf, previousMonth } from "./months";

describe("monthOf", () => {
  it("pega o mês de uma data", () => {
    expect(monthOf("2030-10-07")).toBe("2030-10");
  });
});

describe("previousMonth", () => {
  it("volta um mês e vira o ano em janeiro", () => {
    expect(previousMonth("2030-10")).toBe("2030-09");
    expect(previousMonth("2030-01")).toBe("2029-12");
  });
});

describe("archiveMonths", () => {
  it("agrupa por ano, do mais novo ao mais antigo, só com os meses vividos", () => {
    expect(archiveMonths("2026-10", "2027-02")).toEqual([
      { year: 2027, months: ["2027-02", "2027-01"] },
      { year: 2026, months: ["2026-12", "2026-11", "2026-10"] },
    ]);
  });

  it("tem um mês só quando a partida está no primeiro", () => {
    expect(archiveMonths("2030-10", "2030-10")).toEqual([{ year: 2030, months: ["2030-10"] }]);
  });
});
