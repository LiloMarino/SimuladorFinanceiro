import { describe, expect, it } from "vitest";
import type { GovernmentMonetary } from "@/types";
import { credibilityTone, moveLabel, realRateReading, realRateTone, selicWindow, toPoints } from "./monetary";

const monetary: GovernmentMonetary = {
  by_government: true,
  selic: "0.1075",
  ipca: "0.0450",
  real_rate: "0.0625",
  focus: "0.1075",
  neutral_real_rate: "0.05",
  target: "0.03",
  tolerance: "0.015",
  next_meeting: "2022-02-14",
  cap: "0.03",
  history_selic: "0.1075",
  step: "0.0025",
  floor: "0",
  plan: null,
  credibility: 100,
  credibility_premium: "0",
};

describe("toPoints", () => {
  it("lê a fração em pontos percentuais sem ruído", () => {
    expect(toPoints("0.1075")).toBe(10.75);
    expect(toPoints("0.0025")).toBe(0.25);
  });
});

describe("selicWindow", () => {
  it("vai da SELIC menos o teto à SELIC mais o teto, em passos de 0,25", () => {
    expect(selicWindow(monetary)).toEqual({ min: 7.75, max: 13.75, step: 0.25, selic: 10.75, nearest: 10.75 });
  });

  it("fica na grade de 0,25 quando a SELIC de hoje é a efetiva, fora dela", () => {
    expect(selicWindow({ ...monetary, selic: "0.2365", history_selic: "0.2365" })).toEqual({
      min: 20.75,
      max: 26.5,
      step: 0.25,
      selic: 23.65,
      nearest: 23.75,
    });
  });

  it("nunca passa de zero", () => {
    expect(selicWindow({ ...monetary, selic: "0.0050", history_selic: "0.0050" }).min).toBe(0);
  });

  it("desce a −0,5 com o piso aberto pela deflação", () => {
    const deflation = { ...monetary, selic: "0.0100", history_selic: "0.0050", floor: "-0.005" };
    expect(selicWindow(deflation).min).toBe(-0.5);
    expect(selicWindow({ ...deflation, floor: "0" }).min).toBe(0);
  });

  it("alcança a SELIC da história acima da janela", () => {
    expect(selicWindow({ ...monetary, selic: "0.21", history_selic: "0.25" }).max).toBe(25);
  });

  it("alcança a SELIC da história abaixo da janela", () => {
    expect(selicWindow({ ...monetary, selic: "0.21", history_selic: "0.165" }).min).toBe(16.5);
  });
});

describe("moveLabel", () => {
  it("diz o quanto a decisão mexe na SELIC de hoje", () => {
    expect(moveLabel(11.5, 10.75)).toBe("+0,75 ponto");
    expect(moveLabel(10.75, 10.75)).toBe("mantém");
    expect(moveLabel(9.25, 10.75)).toBe("−1,50 ponto");
  });
});

describe("juro real", () => {
  it("fica neutro entre 2% e 7% e avisa fora da faixa", () => {
    expect(realRateTone("0.0625")).toBe("default");
    expect(realRateTone("0.0150")).toBe("warning");
    expect(realRateTone("0.0800")).toBe("warning");
    expect(realRateReading("0.0150")).toContain("aposentados e investidores");
    expect(realRateReading("0.0800")).toContain("empreendedores");
    expect(realRateReading("0.0625")).toContain("nenhum grupo");
  });
});

describe("credibilityTone", () => {
  it("avisa abaixo de 80 e alerta abaixo de 50", () => {
    expect(credibilityTone(100)).toBe("default");
    expect(credibilityTone(79)).toBe("warning");
    expect(credibilityTone(49)).toBe("destructive");
  });
});
