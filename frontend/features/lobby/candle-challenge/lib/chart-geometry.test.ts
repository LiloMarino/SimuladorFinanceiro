import { describe, expect, it } from "vitest";
import type { ChallengeBar } from "@/types";
import { axisTicks, chartScale, displayTick, HIDDEN_CANDLES, SHOWN_CANDLES } from "./chart-geometry";

const bar = (low: number, high: number): ChallengeBar => ({ open: low, high, low, close: high });

describe("escala do gráfico", () => {
  const scale = chartScale([bar(-10, -5), bar(0, 10)], { width: 770, height: 380 });

  it("põe o maior valor acima do menor", () => {
    expect(scale.y(10)).toBeLessThan(scale.y(-10));
  });

  it("deixa folga: nenhuma máxima ou mínima encosta na borda", () => {
    expect(scale.y(10)).toBeGreaterThan(0);
    expect(scale.y(-10)).toBeLessThan(380);
  });

  it("reserva lugar para as 35 velas, da esquerda para a direita", () => {
    expect(scale.x(0)).toBeLessThan(scale.x(SHOWN_CANDLES - 1));
    expect(scale.x(SHOWN_CANDLES + HIDDEN_CANDLES - 1)).toBeLessThan(770);
    expect(scale.x(1) - scale.x(0)).toBeCloseTo(scale.step);
  });

  it("não quebra com tudo no mesmo preço", () => {
    const flat = chartScale([bar(0, 0)], { width: 770, height: 380 });
    expect(Number.isFinite(flat.y(0))).toBe(true);
  });
});

describe("marcas do eixo", () => {
  it("usa passos redondos dentro do intervalo", () => {
    expect(axisTicks(-12, 18)).toEqual([-10, 0, 10]);
    expect(axisTicks(-3.2, 4.1)).toEqual([-2, 0, 2, 4]);
  });

  it("escreve o sinal e a vírgula", () => {
    expect(displayTick(5)).toBe("+5%");
    expect(displayTick(0)).toBe("0%");
    expect(displayTick(-2.5)).toBe("-2,5%");
  });
});
