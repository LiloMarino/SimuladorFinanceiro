import { describe, expect, it } from "vitest";
import { cellColor, correlationReading, gapReason, valueColor } from "./correlation";

describe("leitura da correlação", () => {
  it("cada faixa começa no seu limite", () => {
    expect(correlationReading(0.7)).toBe("andam muito juntos");
    expect(correlationReading(0.69)).toBe("andam juntos em parte");
    expect(correlationReading(0.3)).toBe("andam juntos em parte");
    expect(correlationReading(-0.3)).toBe("quase independentes");
    expect(correlationReading(-0.31)).toBe("tendem a ir em direções opostas");
  });
});

describe("cores da matriz", () => {
  it("a célula pinta proporcional à força, até 70%", () => {
    expect(cellColor(0)).toBe("color-mix(in oklch, var(--destructive) 0%, transparent)");
    expect(cellColor(0.5)).toBe("color-mix(in oklch, var(--destructive) 35%, transparent)");
    expect(cellColor(-1)).toBe("color-mix(in oklch, var(--chart-1) 70%, transparent)");
  });

  it("o número fica neutro abaixo de 0,1 e satura em 0,7", () => {
    expect(valueColor(0.05)).toBeUndefined();
    expect(valueColor(0.35)).toBe("color-mix(in oklch, var(--destructive) 50%, var(--foreground))");
    expect(valueColor(-0.9)).toBe("color-mix(in oklch, var(--chart-1) 100%, var(--foreground))");
  });
});

describe("motivo de célula vazia", () => {
  it("série parada ou poucos pregões em comum", () => {
    expect(gapReason({ correlation: null, days: 200, reason: "constant_series" }, 60)).toBe(
      "Um dos dois ficou parado na janela: sem variação, não dá pra medir se andam juntos.",
    );
    expect(gapReason({ correlation: null, days: 12, reason: "insufficient_days" }, 60)).toBe(
      "Só 12 pregões em comum (mínimo 60). Aumente a janela ou espere a partida avançar.",
    );
  });
});
