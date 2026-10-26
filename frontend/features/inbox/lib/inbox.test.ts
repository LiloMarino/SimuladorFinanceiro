import { describe, expect, it } from "vitest";
import type { MonthSummary, YearReview } from "@/types";
import { displayRanking, entryTitle } from "./inbox";

describe("entryTitle", () => {
  it("nomeia o mês por extenso no resumo e o ano na retrospectiva", () => {
    // O título só lê o tipo e a data; o resto do conteúdo não entra
    expect(entryTitle({ kind: "YEAR_REVIEW", year: 2002 } as YearReview)).toBe("Retrospectiva de 2002");
    expect(entryTitle({ kind: "MONTH_SUMMARY", month: "2002-11-01" } as MonthSummary)).toBe(
      "Resumo de novembro de 2002",
    );
  });
});

describe("displayRanking", () => {
  it("mostra só a posição no primeiro resumo", () => {
    expect(displayRanking({ position: 2, players: 5, change: null })).toBe("2º de 5");
  });

  it("conta quantas posições subiu ou desceu, no singular e no plural", () => {
    expect(displayRanking({ position: 1, players: 5, change: 2 })).toBe("1º de 5, subiu 2 posições");
    expect(displayRanking({ position: 4, players: 5, change: -1 })).toBe("4º de 5, desceu 1 posição");
    expect(displayRanking({ position: 3, players: 5, change: 0 })).toBe("3º de 5, manteve a posição");
  });
});
