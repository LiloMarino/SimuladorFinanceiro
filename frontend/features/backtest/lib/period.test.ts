import { describe, expect, it } from "vitest";
import { displayEstimate, displaySecondsLeft, displaySpan, weekdaysBetween } from "./period";

describe("weekdaysBetween", () => {
  it("conta só de segunda a sexta, com as duas pontas", () => {
    expect(weekdaysBetween("2024-01-01", "2024-01-07")).toBe(5);
    expect(weekdaysBetween("2024-01-06", "2024-01-07")).toBe(0);
  });
});

describe("displaySpan", () => {
  it("escreve anos e meses", () => {
    expect(displaySpan("2011-01-01", "2027-12-31")).toBe("17 anos");
    expect(displaySpan("2026-11-01", "2027-12-31")).toBe("1 ano e 2 meses");
    expect(displaySpan("2020-01-01", "2020-08-31")).toBe("8 meses");
  });
});

describe("displayEstimate", () => {
  it("escolhe a palavra pela duração", () => {
    expect(displayEstimate(500, 10)).toBe("menos de 1 minuto");
    expect(displayEstimate(2000, 10)).toBe("cerca de 2 minutos");
    expect(displayEstimate(4125, 2)).toBe("cerca de 2 minutos");
    expect(displayEstimate(4125, 10)).toBe("cerca de 4 minutos");
  });
});

describe("displaySecondsLeft", () => {
  it("passa para minutos depois de um minuto e meio", () => {
    expect(displaySecondsLeft(40)).toBe("~40 s");
    expect(displaySecondsLeft(150)).toBe("~3 min");
  });
});
