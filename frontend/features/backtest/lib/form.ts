import { z } from "zod";
import { editValues, type BotFormValues } from "@/shared/lib/bot-form";
import { nameTaken } from "@/shared/lib/bot-names";
import { normalizeNumberString } from "@/shared/lib/utils";
import { dateFieldError, isIsoDate, toIso } from "@/shared/lib/utils/date-field";
import { displayIsoDate, parseLocalDate } from "@/shared/lib/utils/display";
import { moneyToBody, moneyToField } from "@/shared/lib/utils/money-field";
import { draftErrors, fromDraft } from "@/shared/lib/strategy-params";
import type { BacktestConfigRequest, BacktestCoverage, BacktestPriceImpact, BacktestSetup, StrategyInfo } from "@/types";
import { MIN_TRADING_DAYS, weekdaysBetween } from "./period";

/** O teto é o das vagas da sala. */
export const MAX_PARTICIPANTS = 10;
export const BOT_NAME_MAX = 30;

export type BacktestFormValues = {
  name: string;
  startDate: string;
  endDate: string;
  startingCash: string;
  monthlyContribution: string;
  priceImpact: BacktestPriceImpact;
  participants: BotFormValues[];
};

const DEFAULT_STARTING_CASH = "100000.00";
const DEFAULT_CONTRIBUTION = "1000.00";
const DEFAULT_YEARS = 10;

/** Dez anos até onde o mercado é real, sem passar do primeiro dado. */
export function defaultPeriod(coverage: BacktestCoverage) {
  const end = coverage.real_end ?? coverage.generated_end ?? toIso(new Date());
  const start = parseLocalDate(end);
  start.setFullYear(start.getFullYear() - DEFAULT_YEARS);
  const from = toIso(start);
  return { startDate: coverage.first_date && from < coverage.first_date ? coverage.first_date : from, endDate: end };
}

/** A data de início que fixa a faixa dos parâmetros das estratégias. */
export function setupStartDate(setup: BacktestSetup) {
  return setup.config?.start_date ?? defaultPeriod(setup.coverage).startDate;
}

/** O formulário como abre: a configuração do backtest de partida ou, sem ela, o padrão com o nome livre. */
export function formValues(setup: BacktestSetup, strategies: StrategyInfo[]): BacktestFormValues {
  const { config } = setup;
  if (!config) {
    return {
      name: setup.suggested_name,
      ...defaultPeriod(setup.coverage),
      startingCash: moneyToField(DEFAULT_STARTING_CASH),
      monthlyContribution: moneyToField(DEFAULT_CONTRIBUTION),
      priceImpact: "REALISTIC",
      participants: [],
    };
  }
  return {
    name: config.name,
    startDate: config.start_date,
    endDate: config.end_date,
    startingCash: moneyToField(config.starting_cash),
    monthlyContribution: moneyToField(config.monthly_contribution),
    priceImpact: config.price_impact,
    participants: config.participants
      .filter((p) => strategies.some((s) => s.key === p.strategy_key))
      .map((p) =>
        editValues(strategies, {
          nickname: p.nickname,
          color: p.color,
          strategyKey: p.strategy_key,
          params: p.params ?? {},
        }),
      ),
  };
}

/** O primeiro fim que dá pregões suficientes para a nota a partir do início. */
export function earliestEnd(start: string) {
  const day = parseLocalDate(start);
  while (weekdaysBetween(start, toIso(day)) < MIN_TRADING_DAYS) day.setDate(day.getDate() + 1);
  return toIso(day);
}

const dateField = (emptyMessage: string) =>
  z
    .string()
    .min(1, emptyMessage)
    .superRefine((value, ctx) => {
      const message = dateFieldError(value);
      if (message) ctx.addIssue({ code: "custom", message });
    });

/** As regras do formulário: o período dentro do mercado, o dinheiro e as estratégias sem nome ou cor repetidos. */
export function backtestSchema(coverage: BacktestCoverage, strategies: StrategyInfo[]) {
  return z
    .object({
      name: z.string().trim().min(1, "Dê um nome ao backtest."),
      startDate: dateField("Escolha a data de início"),
      endDate: dateField("Escolha a data de fim"),
      startingCash: z
        .string()
        .refine((value) => Number(normalizeNumberString(value)) > 0, "O saldo inicial tem que ser maior que zero"),
      monthlyContribution: z
        .string()
        .refine((value) => value === "" || Number(normalizeNumberString(value)) >= 0, "Use um valor válido"),
      priceImpact: z.enum(["OFF", "REALISTIC", "STRONG"]),
      participants: z
        .array(
          z.object({
            nickname: z.string(),
            strategyKey: z.string(),
            color: z.string(),
            team: z.number().nullable(),
            drafts: z.record(z.string(), z.any()),
          }),
        )
        .min(1, "Falta pelo menos 1 estratégia")
        .max(MAX_PARTICIPANTS, `No máximo ${MAX_PARTICIPANTS} estratégias`),
    })
    .superRefine((data, ctx) => {
      const { first_date: first, generated_end: last } = coverage;
      if (isIsoDate(data.startDate) && first && data.startDate < first)
        ctx.addIssue({
          code: "custom",
          path: ["startDate"],
          message: `O primeiro dado é de ${displayIsoDate(first)}. Comece nesse dia ou depois.`,
        });
      if (isIsoDate(data.endDate) && last && data.endDate > last)
        ctx.addIssue({ code: "custom", path: ["endDate"], message: `O mercado vai até ${displayIsoDate(last)}.` });
      if (isIsoDate(data.startDate) && isIsoDate(data.endDate)) {
        if (data.endDate < data.startDate)
          ctx.addIssue({ code: "custom", path: ["endDate"], message: "O fim vem antes do início." });
        else {
          const days = weekdaysBetween(data.startDate, data.endDate);
          if (days < MIN_TRADING_DAYS)
            ctx.addIssue({
              code: "custom",
              path: ["endDate"],
              message: `Curto demais: este período tem ${days} pregões e a nota precisa de ${MIN_TRADING_DAYS} (uns 3 meses). Termine em ${displayIsoDate(earliestEnd(data.startDate))} ou depois.`,
            });
        }
      }

      data.participants.forEach((participant, index) => {
        const name = participant.nickname.trim();
        const others = data.participants.filter((_, other) => other !== index);
        if (!name || name.length > BOT_NAME_MAX)
          ctx.addIssue({
            code: "custom",
            path: ["participants", index, "nickname"],
            message: name ? `Use até ${BOT_NAME_MAX} letras.` : "Dê um nome à estratégia.",
          });
        else if (
          nameTaken(
            name,
            others.map((o) => o.nickname),
          )
        )
          ctx.addIssue({
            code: "custom",
            path: ["participants", index, "nickname"],
            message: "Outra estratégia já tem esse nome. Sorteie outro ou mude.",
          });
        if (others.some((o) => o.color === participant.color))
          ctx.addIssue({
            code: "custom",
            path: ["participants", index, "color"],
            message: "Outra estratégia já usa essa cor.",
          });
        const strategy = strategies.find((s) => s.key === participant.strategyKey);
        if (strategy && Object.keys(draftErrors(strategy.params, participant.drafts[strategy.key] ?? {})).length > 0)
          ctx.addIssue({
            code: "custom",
            path: ["participants", index, "drafts"],
            message: "Corrija os parâmetros.",
          });
      });
    });
}

/** O pedido ao servidor; nulo enquanto algum parâmetro não está pronto. */
export function toRequest(values: BacktestFormValues, strategies: StrategyInfo[]): BacktestConfigRequest | null {
  const participants: BacktestConfigRequest["participants"] = [];
  for (const participant of values.participants) {
    const strategy = strategies.find((s) => s.key === participant.strategyKey);
    const params = strategy && fromDraft(strategy.params, participant.drafts[strategy.key] ?? {});
    if (!params) return null;
    participants.push({
      nickname: participant.nickname.trim(),
      color: participant.color,
      strategy_key: participant.strategyKey,
      params,
    });
  }
  return {
    name: values.name.trim(),
    start_date: values.startDate,
    end_date: values.endDate,
    starting_cash: moneyToBody(values.startingCash),
    monthly_contribution: moneyToBody(values.monthlyContribution || "0"),
    price_impact: values.priceImpact,
    participants,
  };
}
