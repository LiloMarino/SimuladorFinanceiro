import { z } from "zod";
import { UNEXPECTED_OPTIONS, withdrawalRateToField } from "@/shared/lib/financial-independence";
import { GAME_TYPES } from "@/shared/lib/game-types";
import { NAME_MAX_LENGTH, NAME_TOO_LONG } from "@/shared/lib/name-limit";
import { normalizeNumberString } from "@/shared/lib/utils";
import { dateFieldError, isIsoDate } from "@/shared/lib/utils/date-field";
import { displayDecimal, displayMoneyWhole } from "@/shared/lib/utils/display";
import { moneyToBody, moneyToField } from "@/shared/lib/utils/money-field";
import { VICTORY_CRITERIA } from "@/shared/lib/victory-criteria";
import type {
  ComputerDifficulty,
  CreateSimulationRequest,
  GameType,
  InitialAccount,
  LifeEventEffect,
  LifeEventFamily,
  LifeFrequency,
  PlayerGrouping,
  SalaryMode,
  SelicControl,
  SimulationSettingsData,
  TeamNaming,
  VictoryCriterion,
} from "@/types";
import { FUND_FEE_CAP_MESSAGE, feeCapToBody, feeCapToField, isFeeCap } from "./fund-rules";
import { governmentRuleError } from "./government-rules";
import {
  calculatedGoal,
  isPositiveMoney,
  isWithdrawalRate,
  WITHDRAWAL_RATE_MESSAGE,
  withdrawalRateFraction,
  withdrawalRateToBody,
} from "./life-rules";

// O campo guarda ISO quando a data está completa e real; o texto em digitação é recusado aqui
const dateField = (emptyMessage: string) =>
  z
    .string()
    .min(1, emptyMessage)
    .superRefine((value, ctx) => {
      const message = dateFieldError(value);
      if (message) ctx.addIssue({ code: "custom", message });
    });

const LIFE_EVENT_EFFECTS: readonly LifeEventEffect[] = ["CASH_OUT", "SKIP_NEXT_SALARY", "CASH_IN"];

// A ordem das famílias na tela e a chave de cada uma na frequência da partida
export const LIFE_EVENT_FAMILIES: readonly (readonly [
  LifeEventFamily,
  keyof SimulationSettingsData["life_frequencies"],
])[] = [
  ["EXPENSES", "expenses"],
  ["INCOME", "income"],
  ["GOOD", "good"],
];

export const LIFE_FREQUENCIES: readonly LifeFrequency[] = ["OFF", "RARE", "NORMAL", "FREQUENT"];

const lifeFrequencySchema = z.custom<LifeFrequency>((value) => LIFE_FREQUENCIES.some((level) => level === value));

const LIFE_EVENT_LABEL_MAX_LENGTH = 40;
const LIFE_EVENT_MAX_EXPENSE_MULTIPLE = 24;

const lifeEventSchema = z
  .object({
    key: z.string(),
    label: z.string().trim().min(1, "Dê um nome ao imprevisto").max(LIFE_EVENT_LABEL_MAX_LENGTH, "Nome longo demais"),
    effect: z.custom<LifeEventEffect>((value) => LIFE_EVENT_EFFECTS.some((effect) => effect === value)),
    family: z.custom<LifeEventFamily>((value) => LIFE_EVENT_FAMILIES.some(([family]) => family === value)),
    weight: z.number(),
    // Em despesas mensais, como o host digita: "0,5" é meia despesa
    expenseMultiple: z.string(),
    enabled: z.boolean(),
  })
  .superRefine((event, ctx) => {
    if (event.effect === "SKIP_NEXT_SALARY") return;
    const multiple = Number(normalizeNumberString(event.expenseMultiple));
    if (event.expenseMultiple !== "" && multiple >= 0 && multiple <= LIFE_EVENT_MAX_EXPENSE_MULTIPLE) return;
    ctx.addIssue({
      code: "custom",
      message: `Informe de 0 a ${LIFE_EVENT_MAX_EXPENSE_MULTIPLE} despesas`,
      path: ["expenseMultiple"],
    });
  });

export const simulationFormSchema = z
  .object({
    name: z.string().min(1, "Dê um nome para a partida").max(NAME_MAX_LENGTH, NAME_TOO_LONG),
    startDate: dateField("Escolha a data de início"),
    endDate: dateField("Escolha a data de fim"),
    startingCash: z
      .string()
      .min(1, "O saldo inicial tem que ser maior que zero")
      .refine((val) => Number(normalizeNumberString(val)) > 0, "O saldo inicial tem que ser maior que zero"),
    monthlyContribution: z
      .string()
      .refine((val) => Number(normalizeNumberString(val)) >= 0, "O aporte mensal não pode ser negativo"),
    priceImpactEnabled: z.boolean(),
    priceImpactK: z
      .string()
      .min(1, "Informe a intensidade")
      .refine((val) => Number(normalizeNumberString(val)) >= 0, "A intensidade não pode ser negativa"),
    priceImpactDecayDays: z
      .string()
      .refine((val) => Number.isInteger(Number(val)) && Number(val) >= 1, "Informe ao menos 1 pregão"),
    victoryCriterion: z.custom<VictoryCriterion>((value) => typeof value === "string" && value in VICTORY_CRITERIA),
    gameType: z.custom<GameType>((value) => typeof value === "string" && value in GAME_TYPES),
    goalNetWorth: z
      .string()
      .min(1, "Informe a meta")
      .refine((val) => Number(normalizeNumberString(val)) > 0, "A meta tem que ser maior que zero"),
    monthlySalary: z
      .string()
      .min(1, "Informe o salário")
      .refine(isPositiveMoney, "O salário tem que ser maior que zero"),
    monthlyExpense: z
      .string()
      .min(1, "Informe a despesa")
      .refine(isPositiveMoney, "A despesa tem que ser maior que zero"),
    unexpectedPerYear: z.number().refine((value) => UNEXPECTED_OPTIONS.some((o) => o.perYear === value)),
    lifeEvents: z.array(lifeEventSchema),
    lifeFrequencies: z.object({
      expenses: lifeFrequencySchema,
      income: lifeFrequencySchema,
      good: lifeFrequencySchema,
    }),
    // Percentual ao ano como o jogador digita: "4" é 4%
    withdrawalRate: z
      .string()
      .min(1, "Informe a taxa")
      .refine((val) => isWithdrawalRate(withdrawalRateFraction(val)), WITHDRAWAL_RATE_MESSAGE),
    inflationAdjusted: z.boolean(),
    salaryMode: z.custom<SalaryMode>((value) => value === "EQUAL" || value === "PROFESSIONS"),
    playerGrouping: z.custom<PlayerGrouping>((value) => value === "INDIVIDUAL" || value === "TEAMS"),
    teamNaming: z.custom<TeamNaming>((value) => value === "COLOR" || value === "NUMBER"),
    showEquivalentRate: z.boolean(),
    showMaturityProjection: z.boolean(),
    showChartHints: z.boolean(),
    governmentEnabled: z.boolean(),
    fundsEnabled: z.boolean(),
    // Tetos de taxa das gestoras: o formulário só os carrega, o back valida
    // Teto de cada taxa em percentual, como o host digita ("2" é 2% ao ano)
    fundMaxManagementFee: z.string().refine(isFeeCap, FUND_FEE_CAP_MESSAGE),
    fundMaxPerformanceFee: z.string().refine(isFeeCap, FUND_FEE_CAP_MESSAGE),
    // ISO quando a data está completa; vazio com a expansão desligada
    firstElection: z.string().superRefine((value, ctx) => {
      const message = dateFieldError(value);
      if (message) ctx.addIssue({ code: "custom", message });
    }),
    computerDifficulty: z.custom<ComputerDifficulty>(
      (value) => value === "EASY" || value === "NORMAL" || value === "HARD",
    ),
    pollMargin: z.boolean(),
    initialAccount: z.custom<InitialAccount>((value) => value === "PLAYABLE" || value === "REALISTIC"),
    selicControl: z.custom<SelicControl>((value) => value === "AUTONOMOUS" || value === "GOVERNMENT"),
  })
  .refine((data) => !isIsoDate(data.startDate) || !isIsoDate(data.endDate) || data.endDate > data.startDate, {
    message: "O fim precisa ser depois do início.",
    path: ["endDate"],
  })
  // A expansão pede 5 anos de partida e a primeira eleição dentro dela
  .superRefine((data, ctx) => {
    if (!data.governmentEnabled) return;
    const error = governmentRuleError({ start: data.startDate, end: data.endDate, firstElection: data.firstElection });
    if (error) ctx.addIssue({ code: "custom", message: error.message, path: [error.path] });
  })
  // A vitória política só existe no modo individual
  .superRefine((data, ctx) => {
    if (data.gameType !== "POLITICAL" || data.playerGrouping !== "TEAMS") return;
    ctx.addIssue({
      code: "custom",
      message: "A vitória política vale só no modo todos contra todos.",
      path: ["playerGrouping"],
    });
  })
  // Na corrida a meta fica acima do que o jogador já tem no primeiro dia
  .superRefine((data, ctx) => {
    if (data.gameType !== "GOAL_RACE") return;
    if (Number(normalizeNumberString(data.goalNetWorth)) > Number(normalizeNumberString(data.startingCash))) return;
    ctx.addIssue({
      code: "custom",
      message: `A meta precisa passar do saldo inicial (${data.startingCash}).`,
      path: ["goalNetWorth"],
    });
  })
  // No viver de renda a meta calculada fica acima do que o jogador já tem no primeiro dia
  .superRefine((data, ctx) => {
    if (data.gameType !== "FINANCIAL_INDEPENDENCE") return;
    const goal = calculatedGoal(data.monthlyExpense, data.withdrawalRate);
    if (goal === null || goal > Number(normalizeNumberString(data.startingCash))) return;
    ctx.addIssue({
      code: "custom",
      message: `A meta calculada (${displayMoneyWhole(goal)}) precisa passar do saldo inicial (${data.startingCash}).`,
      path: ["monthlyExpense"],
    });
  });

export type SimulationFormValues = z.infer<typeof simulationFormSchema>;

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
    lifeEvents: settings.life_events.map((event) => ({
      key: event.key,
      label: event.label,
      effect: event.effect,
      family: event.family,
      weight: event.weight,
      expenseMultiple: displayDecimal(Number(event.expense_multiple)),
      enabled: event.enabled,
    })),
    lifeFrequencies: settings.life_frequencies,
    withdrawalRate: withdrawalRateToField(settings.withdrawal_rate),
    inflationAdjusted: settings.inflation_adjusted,
    salaryMode: settings.salary_mode,
    playerGrouping: settings.player_grouping,
    teamNaming: settings.team_naming,
    showEquivalentRate: settings.show_equivalent_rate,
    showMaturityProjection: settings.show_maturity_projection,
    showChartHints: settings.show_chart_hints,
    governmentEnabled: settings.government_enabled,
    fundsEnabled: settings.funds_enabled,
    fundMaxManagementFee: feeCapToField(settings.fund_max_management_fee),
    fundMaxPerformanceFee: feeCapToField(settings.fund_max_performance_fee),
    firstElection: settings.first_election ?? "",
    computerDifficulty: settings.computer_difficulty,
    pollMargin: settings.poll_margin,
    initialAccount: settings.initial_account,
    selicControl: settings.selic_control,
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
    life_events: values.lifeEvents.map((event) => ({
      key: event.key,
      label: event.label.trim(),
      effect: event.effect,
      family: event.family,
      weight: event.weight,
      // O corte do salário não usa valor
      expense_multiple: event.effect === "SKIP_NEXT_SALARY" ? "0" : normalizeNumberString(event.expenseMultiple),
      enabled: event.enabled,
    })),
    life_frequencies: values.lifeFrequencies,
    withdrawal_rate: withdrawalRateToBody(values.withdrawalRate),
    inflation_adjusted: values.inflationAdjusted,
    salary_mode: values.salaryMode,
    player_grouping: values.playerGrouping,
    team_naming: values.teamNaming,
    show_equivalent_rate: values.showEquivalentRate,
    show_maturity_projection: values.showMaturityProjection,
    show_chart_hints: values.showChartHints,
    government_enabled: values.governmentEnabled,
    funds_enabled: values.fundsEnabled,
    fund_max_management_fee: feeCapToBody(values.fundMaxManagementFee),
    fund_max_performance_fee: feeCapToBody(values.fundMaxPerformanceFee),
    first_election: values.governmentEnabled && values.firstElection ? values.firstElection : null,
    computer_difficulty: values.computerDifficulty,
    poll_margin: values.pollMargin,
    initial_account: values.initialAccount,
    // A SELIC do governo depende da expansão; desligada, a partida volta ao Banco Central autônomo
    selic_control: values.governmentEnabled ? values.selicControl : "AUTONOMOUS",
  };
}
