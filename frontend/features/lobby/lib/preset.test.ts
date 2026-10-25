import { describe, expect, it } from "vitest";
import type { Preset } from "@/types";
import { changedGroups, lowercaseGroups, presetSummary } from "./preset";

const preset = (overrides: Partial<Preset>): Preset => ({
  id: 1,
  name: "Teste",
  built_in: true,
  created_at: "2026-10-18T12:00:00Z",
  config: {},
  ...overrides,
});

describe("resumo do preset", () => {
  it("pronto clássico: anos, saldo e aporte, e o que decide a partida", () => {
    // 2010-01-01 → 2024-12-31 são 15 anos
    const clasico = preset({
      config: {
        start_date: "2010-01-01",
        end_date: "2024-12-31",
        starting_cash: "100000",
        monthly_contribution: "1000",
        game_type: "CLASSIC",
        victory_criterion: "SCORE",
      },
    });
    expect(presetSummary(clasico)).toBe("15 anos · R$ 100 mil + R$ 1.000/mês · Nota geral");
  });

  it("pronto de viver de renda: impacto de preço e Especialista quando as duas ajudas estão desligadas", () => {
    const realista = preset({
      config: {
        start_date: "2000-01-01",
        end_date: "2024-12-31",
        game_type: "FINANCIAL_INDEPENDENCE",
        price_impact_enabled: true,
        show_equivalent_rate: false,
        show_maturity_projection: false,
        show_chart_hints: false,
      },
    });
    expect(presetSummary(realista)).toBe("25 anos · viver de renda · impacto de preço · Especialista");
  });

  it("preset do host: a data em que foi salvo, os anos do período e o tipo", () => {
    const sexta = preset({
      built_in: false,
      created_at: "2026-10-18T12:00:00Z",
      config: { start_date: "2010-01-01", end_date: "2024-12-31", player_grouping: "TEAMS" },
    });
    expect(presetSummary(sexta)).toBe("salvo em 18/10/2026 · 2010 → 2024 · em equipes");

    const corrida = preset({
      built_in: false,
      created_at: "2026-10-21T12:00:00Z",
      config: { start_date: "2019-01-01", end_date: "2023-12-31", game_type: "GOAL_RACE" },
    });
    expect(presetSummary(corrida)).toBe("salvo em 21/10/2026 · 2019 → 2023 · corrida à meta");
  });
});

describe("grupos de regras", () => {
  it("lista o que mudou com a inicial maiúscula e as ajudas em minúsculas", () => {
    expect(changedGroups(["STARTING_CASH", "VICTORY"])).toBe("Saldo inicial e Quem vence");
    expect(lowercaseGroups(["ASSISTANCES", "PRICE_IMPACT"])).toBe("assistências e mercado");
  });
});
