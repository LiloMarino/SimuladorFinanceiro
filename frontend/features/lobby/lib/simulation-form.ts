import { withdrawalRateToField } from "@/shared/lib/financial-independence";
import { normalizeNumberString } from "@/shared/lib/utils";
import { displayDecimal } from "@/shared/lib/utils/display";
import { moneyToBody, moneyToField } from "@/shared/lib/utils/money-field";
import type { CreateSimulationRequest, SimulationSettingsData } from "@/types";
import type { SimulationFormValues } from "../components/lobby-match";
import { withdrawalRateToBody } from "./life-rules";

/** As regras da partida como o formulário do lobby as mostra. */
export function toFormValues(settings: SimulationSettingsData): SimulationFormValues {
  return {
    name: settings.name,
    startDate: settings.start_date,
    endDate: settings.end_date,
    startingCash: moneyToField(settings.starting_cash),
    monthlyContribution: moneyToField(settings.monthly_contribution),
    priceImpactEnabled: settings.price_impact_enabled,
    priceImpactK: displayDecimal(settings.price_impact_k),
    priceImpactDecayDays: String(settings.price_impact_decay_days),
    victoryCriterion: settings.victory_criterion,
    gameType: settings.game_type,
    goalNetWorth: moneyToField(settings.goal_net_worth),
    monthlySalary: moneyToField(settings.monthly_salary),
    monthlyExpense: moneyToField(settings.monthly_expense),
    unexpectedPerYear: settings.unexpected_per_year,
    withdrawalRate: withdrawalRateToField(settings.withdrawal_rate),
    inflationAdjusted: settings.inflation_adjusted,
    playerGrouping: settings.player_grouping,
    teamNaming: settings.team_naming,
    showEquivalentRate: settings.show_equivalent_rate,
    showMaturityProjection: settings.show_maturity_projection,
    showChartHints: settings.show_chart_hints,
    governmentEnabled: settings.government_enabled,
    firstElection: settings.first_election ?? "",
    computerDifficulty: settings.computer_difficulty,
  };
}

/**
 * O formulário do lobby como corpo da API, para criar a partida e para sincronizar as regras.
 * As chaves seguem a ordem do SimulationSettingsData: o hook de sincronização descarta duplicata comparando o JSON.
 */
export function toSettingsBody(values: SimulationFormValues): CreateSimulationRequest {
  return {
    name: values.name,
    start_date: values.startDate,
    end_date: values.endDate,
    starting_cash: moneyToBody(values.startingCash),
    monthly_contribution: moneyToBody(values.monthlyContribution),
    price_impact_enabled: values.priceImpactEnabled,
    price_impact_k: Number(normalizeNumberString(values.priceImpactK)),
    price_impact_decay_days: Number(values.priceImpactDecayDays),
    victory_criterion: values.victoryCriterion,
    game_type: values.gameType,
    goal_net_worth: moneyToBody(values.goalNetWorth),
    monthly_salary: moneyToBody(values.monthlySalary),
    monthly_expense: moneyToBody(values.monthlyExpense),
    unexpected_per_year: values.unexpectedPerYear,
    withdrawal_rate: withdrawalRateToBody(values.withdrawalRate),
    inflation_adjusted: values.inflationAdjusted,
    player_grouping: values.playerGrouping,
    team_naming: values.teamNaming,
    show_equivalent_rate: values.showEquivalentRate,
    show_maturity_projection: values.showMaturityProjection,
    show_chart_hints: values.showChartHints,
    government_enabled: values.governmentEnabled,
    first_election: values.governmentEnabled && values.firstElection ? values.firstElection : null,
    computer_difficulty: values.computerDifficulty,
  };
}
