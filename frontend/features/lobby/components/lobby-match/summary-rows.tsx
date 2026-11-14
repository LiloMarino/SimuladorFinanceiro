import type { ReactNode } from "react";
import { ExpansionEmblem } from "@/shared/components/expansion-emblem";
import { GroupingBadge } from "@/shared/components/grouping-badge";
import { Badge } from "@/shared/components/ui/badge";
import { summarizeAssistances } from "@/shared/lib/assistance";
import { EXPANSIONS } from "@/shared/lib/expansions";
import { displayRatePercent, unexpectedLabel } from "@/shared/lib/financial-independence";
import { GAME_TYPES } from "@/shared/lib/game-types";
import { PRICE_IMPACT_MODE_LABELS, priceImpactModeOf } from "@/shared/lib/price-impact";
import { normalizeNumberString } from "@/shared/lib/utils";
import { isIsoDate } from "@/shared/lib/utils/date-field";
import { displayDate, displayMoneyCompact, displayMoneyWhole, parseLocalDate } from "@/shared/lib/utils/display";
import { VICTORY_CRITERIA } from "@/shared/lib/victory-criteria";
import type { SimulationSettings } from "@/types";
import { COMPUTER_DIFFICULTIES } from "../../lib/government-rules";
import { calculatedGoal, withdrawalRateFraction } from "../../lib/life-rules";
import type { SimulationFormValues } from "../../lib/simulation-form";

export type SummaryRow = { label: string; value: ReactNode };

/** As linhas do que só existe no tipo escolhido: o critério, a meta fixa ou a vida real. */
function typeRows(rules: SimulationFormValues): SummaryRow[] {
  if (rules.gameType === "FINANCIAL_INDEPENDENCE") {
    const goal = calculatedGoal(rules.monthlyExpense, rules.withdrawalRate);
    const activeLifeEvents = rules.lifeEvents.filter((event) => event.enabled).length;
    return [
      {
        label: "Salário · despesa",
        value: (
          <span className="font-mono">
            {displayMoneyWhole(Number(normalizeNumberString(rules.monthlySalary)))} ·{" "}
            {displayMoneyWhole(Number(normalizeNumberString(rules.monthlyExpense)))}
          </span>
        ),
      },
      {
        label: "Meta",
        value: (
          <span>
            <span className="font-mono">{goal === null ? "—" : displayMoneyCompact(goal)}</span> ·{" "}
            {displayRatePercent(withdrawalRateFraction(rules.withdrawalRate))} ao ano
          </span>
        ),
      },
      {
        label: "Imprevistos",
        value: `${unexpectedLabel(rules.unexpectedPerYear)} · ${rules.unexpectedPerYear} por ano · ${activeLifeEvents} de ${rules.lifeEvents.length} tipos`,
      },
      {
        label: "Inflação",
        value: rules.inflationAdjusted ? "Corrigido pelo IPCA" : "Reais fixos",
      },
    ];
  }

  if (rules.gameType === "CLASSIC") {
    return [
      { label: "Vitória por", value: <Badge variant="info">{VICTORY_CRITERIA[rules.victoryCriterion].label}</Badge> },
    ];
  }

  if (rules.gameType === "POLITICAL") {
    return [{ label: "Vitória por", value: <Badge variant="info">Partido com mais capital político</Badge> }];
  }

  // A meta com o múltiplo do saldo inicial quando ele é redondo: "R$ 1.000.000,00 · 10× o saldo"
  const startingCash = Number(normalizeNumberString(rules.startingCash));
  const multiple = startingCash > 0 ? Number(normalizeNumberString(rules.goalNetWorth)) / startingCash : NaN;
  const goalSummary = Number.isInteger(multiple) ? `${rules.goalNetWorth} · ${multiple}× o saldo` : rules.goalNetWorth;
  return [{ label: "Meta", value: <span className="font-mono">{goalSummary}</span> }];
}

/** As regras da partida em linhas de rótulo e valor; o preset entra quando as regras são as da nova partida. */
export function summaryRows(rules: SimulationFormValues, preset: SimulationSettings["applied_preset"]): SummaryRow[] {
  const impactMode = priceImpactModeOf(rules.priceImpactEnabled, rules.priceImpactK, rules.priceImpactDecayDays);
  const assistances = summarizeAssistances([
    rules.showEquivalentRate,
    rules.showMaturityProjection,
    rules.showChartHints,
  ]);

  return [
    ...(preset
      ? [
          {
            label: "Preset",
            value: (
              <span className="flex items-center justify-end gap-1.5">
                <Badge variant="info" className="min-w-0">
                  <span className="truncate">{preset.name}</span>
                </Badge>
                {preset.changed.length > 0 && <Badge variant="warning">modificado</Badge>}
              </span>
            ),
          },
        ]
      : []),
    { label: "Nome", value: rules.name },
    {
      label: "Período",
      value: (
        <span className="font-mono">
          {isIsoDate(rules.startDate) ? displayDate(parseLocalDate(rules.startDate)) : "—"} →{" "}
          {isIsoDate(rules.endDate) ? displayDate(parseLocalDate(rules.endDate)) : "—"}
        </span>
      ),
    },
    { label: "Saldo inicial", value: <span className="font-mono">{rules.startingCash}</span> },
    ...(rules.gameType === "FINANCIAL_INDEPENDENCE"
      ? []
      : [{ label: "Aporte mensal", value: <span className="font-mono">{rules.monthlyContribution}</span> }]),
    { label: "Modo", value: <GroupingBadge grouping={rules.playerGrouping} /> },
    { label: "Tipo de partida", value: <Badge variant="info">{GAME_TYPES[rules.gameType]?.label}</Badge> },
    ...typeRows(rules),
    {
      label: "Expansões",
      value:
        rules.governmentEnabled || rules.fundsEnabled ? (
          <span className="flex flex-wrap gap-1.5">
            {rules.governmentEnabled && (
              <Badge variant="outline">
                <ExpansionEmblem expansion="government" size="xs" />
                {EXPANSIONS.government.label}
              </Badge>
            )}
            {rules.fundsEnabled && (
              <Badge variant="outline">
                <ExpansionEmblem expansion="funds" size="xs" />
                {EXPANSIONS.funds.label}
              </Badge>
            )}
          </span>
        ) : (
          <span className="text-muted-foreground">—</span>
        ),
    },
    ...(rules.governmentEnabled && isIsoDate(rules.firstElection)
      ? [
          {
            label: "Primeira eleição",
            value: (
              <span>
                <span className="font-mono">{displayDate(parseLocalDate(rules.firstElection))}</span> · computador{" "}
                {COMPUTER_DIFFICULTIES.find((d) => d.value === rules.computerDifficulty)?.label.toLowerCase()}
              </span>
            ),
          },
        ]
      : []),
    {
      label: "Impacto de preço",
      value: (
        <span className="flex items-center gap-2">
          <Badge variant={impactMode === "OFF" ? "secondary" : "info"}>{PRICE_IMPACT_MODE_LABELS[impactMode]}</Badge>
          {impactMode !== "OFF" && (
            <span className="font-mono text-xs text-muted-foreground">
              k {rules.priceImpactK} · T {rules.priceImpactDecayDays}
            </span>
          )}
        </span>
      ),
    },
    {
      label: "Assistências",
      value: (
        <Badge
          variant={assistances.mode === "NORMAL" ? "secondary" : assistances.mode === "EXPERT" ? "inverse" : "info"}
        >
          {assistances.mode === "NORMAL" && "Normal"}
          {assistances.mode === "EXPERT" && "Especialista"}
          {assistances.mode === "CUSTOM" && `Personalizado · ${assistances.shown} de ${assistances.total} ligadas`}
        </Badge>
      ),
    },
  ];
}
