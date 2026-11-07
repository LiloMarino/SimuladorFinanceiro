import { describe, expect, it } from "vitest";
import { isUrgent, secondsLeft, timeFraction } from "./countdown";

describe("cronômetro da pergunta", () => {
  it("arredonda os segundos para cima", () => {
    expect(secondsLeft(6000)).toBe(6);
    expect(secondsLeft(5001)).toBe(6);
    expect(secondsLeft(1)).toBe(1);
    expect(secondsLeft(0)).toBe(0);
    expect(secondsLeft(-40)).toBe(0);
  });

  it("fica urgente nos 2 s finais", () => {
    expect(isUrgent(2001)).toBe(false);
    expect(isUrgent(2000)).toBe(true);
    expect(isUrgent(0)).toBe(true);
  });

  it("mede a barra entre 0 e 1", () => {
    expect(timeFraction(6000, 8000)).toBe(0.75);
    expect(timeFraction(9000, 8000)).toBe(1);
    expect(timeFraction(-1, 8000)).toBe(0);
    expect(timeFraction(100, 0)).toBe(0);
  });
});
