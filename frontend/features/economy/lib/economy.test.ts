import { describe, expect, it } from "vitest";
import type { EconomyPanel } from "@/types";
import { copomLabel, economyRows, ipcaExample, lastCopomNote, selicExample, targetNote } from "./economy";

const point = (date: string, selic: string, ipca: string, target = "0.035") => ({
  tolerance: "0.015",
  date,
  selic,
  ipca,
  real_rate: String(Number(selic) - Number(ipca)),
  target,
});

const rise = { date: "2022-03-16", change: "0.0075", selic: "0.1075" };

describe("economyRows", () => {
  it("liga a mudança do Copom ao ponto do mesmo dia", () => {
    const panel: EconomyPanel = {
      points: [point("2022-02-28", "0.1", "0.05"), point("2022-03-16", "0.1075", "0.06")],
      copom_changes: [rise],
    };
    const [first, second] = economyRows(panel);
    expect(first?.copom).toBeUndefined();
    expect(second?.copom).toEqual(rise);
    // 10,75% de SELIC com 6% de IPCA
    expect(second?.realRate).toBeCloseTo(0.0475, 6);
  });
});

describe("copomLabel", () => {
  it("diz o tamanho e o novo nível quando sobe", () => {
    expect(copomLabel(rise)).toBe("Copom subiu a SELIC em 0,75 p.p., para 10,75%");
  });

  it("diz baixou quando a mudança é negativa", () => {
    expect(copomLabel({ date: "2022-05-04", change: "-0.005", selic: "0.1025" })).toBe(
      "Copom baixou a SELIC em 0,50 p.p., para 10,25%",
    );
  });
});

describe("economyRows", () => {
  const panel: EconomyPanel = {
    points: [
      point("2021-01-29", "0.02", "0.03"),
      point("2022-03-16", "0.1075", "0.06"),
      point("2022-04-29", "0.11", "0.06"),
    ],
    copom_changes: [],
  };

  it("monta a faixa da meta com a tolerância para os dois lados", () => {
    const [first] = economyRows(panel);
    // meta de 3,5% ± 1,5 ponto: de 2% a 5%
    expect(first?.band[0]).toBeCloseTo(0.02, 6);
    expect(first?.band[1]).toBeCloseTo(0.05, 6);
  });

  it("no recorte de 12 meses deixa só os pontos do último ano", () => {
    expect(economyRows(panel, "year").map((row) => row.selic)).toEqual([0.1075, 0.11]);
  });
});

describe("lastCopomNote", () => {
  it("avisa quando a SELIC ainda não mudou", () => {
    expect(lastCopomNote([])).toBe("Sem mudança do Copom ainda");
  });

  it("mostra o sentido, o tamanho e o mês da última mudança", () => {
    expect(lastCopomNote([rise])).toBe("▲ 0,75 p.p. em mar/22");
  });
});

describe("exemplos em reais", () => {
  it("a SELIC de 10,75% rende R$ 10,75 em R$ 100", () => {
    const text = selicExample(point("2022-03-16", "0.1075", "0.06"));
    expect(text).toContain("110,75");
  });

  it("o IPCA de 6% faz R$ 100 custarem R$ 106", () => {
    expect(ipcaExample(point("2022-03-16", "0.1075", "0.06"))).toContain("106,00");
  });
});

describe("targetNote", () => {
  it("diz a meta do ano", () => {
    expect(targetNote(point("2022-03-16", "0.1", "0.06"))).toBe("meta de 3,50%");
  });
});
