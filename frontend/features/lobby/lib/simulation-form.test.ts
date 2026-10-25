import { describe, expect, it } from "vitest";
import type { SimulationSettingsData } from "@/types";
import { toFormValues, toSettingsBody } from "./simulation-form";

// Regras como a API devolve: dinheiro com duas casas e a taxa com quatro
const settings: SimulationSettingsData = {
  name: "Simulação #2",
  start_date: "2000-01-01",
  end_date: "2026-01-01",
  starting_cash: "10000.00",
  monthly_contribution: "500.00",
  price_impact_enabled: true,
  price_impact_k: 0.02,
  price_impact_decay_days: 20,
  victory_criterion: "SHARPE",
  game_type: "FINANCIAL_INDEPENDENCE",
  goal_net_worth: "100000.00",
  monthly_salary: "8000.00",
  monthly_expense: "5000.00",
  unexpected_per_year: 3,
  withdrawal_rate: "0.0400",
  inflation_adjusted: true,
  player_grouping: "TEAMS",
  team_naming: "NUMBER",
  show_equivalent_rate: false,
  show_maturity_projection: true,
  show_chart_hints: false,
  government_enabled: false,
  first_election: null,
  computer_difficulty: "NORMAL",
};

describe("regras da partida ↔ formulário do lobby", () => {
  it("ida e volta devolve as mesmas regras, na mesma ordem de chaves", () => {
    const body = toSettingsBody(toFormValues(settings));
    expect(body).toEqual(settings);
    expect(Object.keys(body)).toEqual(Object.keys(settings));
  });

  it("a primeira eleição só segue no corpo com a expansão ligada", () => {
    const values = { ...toFormValues(settings), governmentEnabled: false, firstElection: "2010-10-07" };
    expect(toSettingsBody(values).first_election).toBeNull();
    expect(toSettingsBody({ ...values, governmentEnabled: true }).first_election).toBe("2010-10-07");
  });

  it("o formulário mostra o dinheiro com a máscara e a taxa em percentual", () => {
    const values = toFormValues(settings);
    expect(values.startingCash).toBe("R$ 10.000,00");
    expect(values.priceImpactK).toBe("0,02");
    expect(values.withdrawalRate).toBe("4");
  });

  it("o corpo leva o dinheiro em centavos, truncado", () => {
    const values = { ...toFormValues(settings), startingCash: "1.234,567", monthlyContribution: "" };
    const body = toSettingsBody(values);
    expect(body.starting_cash).toBe("1234.56");
    expect(body.monthly_contribution).toBe("0.00");
  });
});
