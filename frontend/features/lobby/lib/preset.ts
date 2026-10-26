import { displayIsoDate, displayMoneyWhole, parseLocalDate } from "@/shared/lib/utils/display";
import { summarizeAssistances } from "@/shared/lib/assistance";
import { EXPANSIONS } from "@/shared/lib/expansions";
import { GAME_TYPES, winRuleLabel } from "@/shared/lib/game-types";
import { isIsoDate } from "@/shared/lib/utils/date-field";
import { VICTORY_CRITERIA } from "@/shared/lib/victory-criteria";
import type { Preset, PresetRuleGroup, SimulationSettingsData } from "@/types";
import type { SimulationFormValues } from "../components/lobby-match";
import { joinNames } from "./join-names";
import { PRICE_IMPACT_MODE_LABELS, priceImpactModeOf } from "@/shared/lib/price-impact";

/** O servidor recusa com 409 o nome que outro preset já usa */
export const NAME_TAKEN_STATUS = 409;
export const NAME_TAKEN_MESSAGE = "Já existe um preset com esse nome.";
export const PRESET_NAME_MAX = 60;

/** Como o painel chama cada grupo de regras */
export const RULE_GROUP_LABELS: Record<PresetRuleGroup, string> = {
  PERIOD: "Período",
  STARTING_CASH: "Saldo inicial",
  MONTHLY_CONTRIBUTION: "Aporte mensal",
  GROUPING: "Modo de jogo",
  GAME_TYPE: "Tipo de partida",
  VICTORY: "Quem vence",
  GOAL: "Meta",
  LIFE: "Vida real",
  ASSISTANCES: "Assistências",
  PRICE_IMPACT: "Mercado",
  EXPANSIONS: "Expansões",
};

// O servidor guarda as regras do preset como JSON livre: campo que o preset não traz fica de fora
type PresetRules = Partial<SimulationSettingsData>;
const rulesOf = (preset: Preset) => preset.config as PresetRules;

const nbspToSpace = (text: string) => text.replace(/ /g, " ");

/** "Salvo antes de assistências e mercado" lista os grupos em minúsculas, na ordem em que chegam */
export function lowercaseGroups(groups: PresetRuleGroup[]) {
  return joinNames(groups.map((group) => RULE_GROUP_LABELS[group].toLowerCase()));
}

/** "Mudou desde que carregou: Saldo inicial e Quem vence" */
export function changedGroups(groups: PresetRuleGroup[]) {
  return joinNames(groups.map((group) => RULE_GROUP_LABELS[group]));
}

/** "R$ 100 mil" para os milhares redondos que um saldo costuma ser; o resto em reais inteiros */
function moneyShort(value: number) {
  return value >= 1000 && value % 1000 === 0
    ? `R$ ${(value / 1000).toLocaleString("pt-BR")} mil`
    : displayMoneyWhole(value);
}

function yearsOf(rules: PresetRules) {
  if (!rules.start_date || !rules.end_date) return null;
  const days = (parseLocalDate(rules.end_date).getTime() - parseLocalDate(rules.start_date).getTime()) / 86_400_000;
  return Math.round(days / 365.25);
}

/** O que decide a partida em palavras curtas: "em equipes" antes do tipo */
function tagOf(rules: PresetRules) {
  if (rules.player_grouping === "TEAMS") return "em equipes";
  const gameType = rules.game_type ?? "CLASSIC";
  return gameType === "CLASSIC"
    ? winRuleLabel(gameType, rules.victory_criterion ?? "SCORE")
    : (GAME_TYPES[gameType]?.label.toLowerCase() ?? gameType);
}

/** Os prontos descrevem o jogo ("15 anos · R$ 100 mil + R$ 1.000/mês · Nota geral"); os do host dizem quando foram salvos. */
export function presetSummary(preset: Preset) {
  const rules = rulesOf(preset);

  if (!preset.built_in) {
    const period =
      rules.start_date && rules.end_date ? [`${rules.start_date.slice(0, 4)} → ${rules.end_date.slice(0, 4)}`] : [];
    return [`salvo em ${displayIsoDate(preset.created_at.slice(0, 10))}`, ...period, tagOf(rules)].join(" · ");
  }

  const years = yearsOf(rules);
  const parts = years === null ? [] : [`${years} anos`];
  const gameType = rules.game_type ?? "CLASSIC";
  if (gameType === "FINANCIAL_INDEPENDENCE") {
    parts.push("viver de renda");
    if (rules.price_impact_enabled) parts.push("impacto de preço");
    if (
      rules.show_equivalent_rate === false &&
      rules.show_maturity_projection === false &&
      rules.show_chart_hints === false
    ) {
      parts.push("Especialista");
    }
  } else {
    if (rules.starting_cash) {
      parts.push(
        `${moneyShort(Number(rules.starting_cash))} + ${displayMoneyWhole(rules.monthly_contribution ?? 0)}/mês`,
      );
    }
    parts.push(tagOf(rules));
  }
  return nbspToSpace(parts.join(" · "));
}

const GROUPING_LABELS: Record<SimulationFormValues["playerGrouping"], string> = {
  INDIVIDUAL: "Todos contra todos",
  TEAMS: "Em equipes",
};

/** O que o preset guarda das regras de agora, na ordem do diálogo de salvar */
export function presetIncludes(values: SimulationFormValues): { label: string; value: string }[] {
  const independence = values.gameType === "FINANCIAL_INDEPENDENCE";
  const assistances = summarizeAssistances([
    values.showEquivalentRate,
    values.showMaturityProjection,
    values.showChartHints,
  ]);
  const impact = priceImpactModeOf(values.priceImpactEnabled, values.priceImpactK, values.priceImpactDecayDays);

  const decides =
    values.gameType === "CLASSIC"
      ? { label: "Quem vence", value: VICTORY_CRITERIA[values.victoryCriterion].label }
      : independence
        ? { label: "Vida real", value: `Salário ${values.monthlySalary} · despesa ${values.monthlyExpense}` }
        : { label: "Meta", value: values.goalNetWorth };

  return [
    {
      label: "Período",
      value:
        isIsoDate(values.startDate) && isIsoDate(values.endDate)
          ? `${displayIsoDate(values.startDate)} → ${displayIsoDate(values.endDate)}`
          : "—",
    },
    {
      label: "Modo e tipo",
      value: `${GROUPING_LABELS[values.playerGrouping]} · ${GAME_TYPES[values.gameType]?.label}`,
    },
    {
      label: "Saldo e aporte",
      value: independence ? values.startingCash : `${values.startingCash} + ${values.monthlyContribution}/mês`,
    },
    decides,
    {
      label: "Assistências",
      value:
        assistances.mode === "NORMAL"
          ? "Todas ligadas"
          : assistances.mode === "EXPERT"
            ? "Modo Especialista"
            : `Personalizado · ${assistances.shown} de ${assistances.total} ligadas`,
    },
    {
      label: "Mercado",
      value: impact === "OFF" ? "Impacto de preço desligado" : `Impacto de preço · ${PRICE_IMPACT_MODE_LABELS[impact]}`,
    },
    {
      label: RULE_GROUP_LABELS.EXPANSIONS,
      value: values.governmentEnabled ? EXPANSIONS.government.label : "Nenhuma",
    },
  ];
}
