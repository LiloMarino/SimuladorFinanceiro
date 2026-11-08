import { describe, expect, it } from "vitest";
import { readingDay } from "./reading";

describe("readingDay", () => {
  const sections = [
    { day: "2030-10-06", top: 300 },
    { day: "2030-10-05", top: 600 },
    { day: "2030-10-04", top: 900 },
  ];

  it("é nulo enquanto nenhum dia chegou à linha", () => {
    expect(readingDay(sections, 100)).toBeNull();
  });

  it("conta o dia cujo título está exatamente na linha", () => {
    expect(readingDay(sections, 300)).toBe("2030-10-06");
  });

  it("fica com o último dia que passou da linha", () => {
    expect(readingDay(sections, 750)).toBe("2030-10-05");
    expect(readingDay(sections, 5000)).toBe("2030-10-04");
  });

  it("é nulo sem dias na lista", () => {
    expect(readingDay([], 300)).toBeNull();
  });
});
