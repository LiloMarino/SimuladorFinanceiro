import { describe, expect, it } from "vitest";
import type { SimulationSettingsData } from "@/types";
import { NAME_MAX_LENGTH } from "@/shared/lib/name-limit";
import { simulationFormSchema, toFormValues, toSettingsBody } from "./simulation-form";

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
  life_events: [
    { key: "REPAIR", label: "Conserto do carro", effect: "CASH_OUT", weight: 3, expense_multiple: "2", enabled: true },
    { key: "HEALTH", label: "Despesa de saúde", effect: "CASH_OUT", weight: 2, expense_multiple: "2", enabled: false },
    { key: "LAYOFF", label: "Demissão", effect: "SKIP_NEXT_SALARY", weight: 1, expense_multiple: "0", enabled: true },
    { key: "custom-1a2b3c4d", label: "Multa", effect: "CASH_OUT", weight: 1, expense_multiple: "0.5", enabled: true },
  ],
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
  poll_margin: false,
  initial_account: "REALISTIC",
  selic_control: "AUTONOMOUS",
};

describe("regras da partida ↔ formulário do lobby", () => {
  it("ida e volta devolve as mesmas regras, na mesma ordem de chaves", () => {
    const body = toSettingsBody(toFormValues(settings));
    expect(body).toEqual(settings);
    expect(Object.keys(body)).toEqual(Object.keys(settings));
  });

  it("o valor do imprevisto aparece em despesas mensais com vírgula", () => {
    const values = toFormValues(settings);
    expect(values.lifeEvents.map((event) => event.expenseMultiple)).toEqual(["2", "2", "0", "0,5"]);
  });

  it("o corte de salário vai sem valor no corpo", () => {
    const values = toFormValues(settings);
    const lifeEvents = values.lifeEvents.map((event) => ({ ...event, expenseMultiple: "9" }));
    const body = toSettingsBody({ ...values, lifeEvents });
    expect(body.life_events?.find((event) => event.key === "LAYOFF")?.expense_multiple).toBe("0");
    expect(body.life_events?.find((event) => event.key === "REPAIR")?.expense_multiple).toBe("9");
  });

  it("recusa tipo sem nome ou com valor fora de 0 a 24 despesas", () => {
    const values = toFormValues(settings);
    const [repair, ...rest] = values.lifeEvents;
    if (!repair) throw new Error("sem tipos");
    const parse = (event: typeof repair) => simulationFormSchema.safeParse({ ...values, lifeEvents: [event, ...rest] });
    expect(parse(repair).success).toBe(true);
    expect(parse({ ...repair, label: "  " }).success).toBe(false);
    expect(parse({ ...repair, expenseMultiple: "25" }).success).toBe(false);
    expect(parse({ ...repair, expenseMultiple: "" }).success).toBe(false);
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

describe("nome da partida", () => {
  const nameIssue = (name: string) =>
    simulationFormSchema
      .safeParse({ ...toFormValues(settings), name })
      .error?.issues.find((issue) => issue.path[0] === "name");

  it("aceita até o limite e recusa um caractere a mais", () => {
    expect(nameIssue("a".repeat(NAME_MAX_LENGTH))).toBeUndefined();
    expect(nameIssue("a".repeat(NAME_MAX_LENGTH + 1))?.message).toBe(`Use até ${NAME_MAX_LENGTH} caracteres.`);
  });
});
