import { PLAYER_COLORS } from "@/shared/lib/player-colors";
import { defaultValues, toDraft, type ParamDraft, type ParamValues } from "@/shared/lib/strategy-params";
import type { RoomPlayer, StrategyInfo } from "@/types";
import { drawBotName } from "./bot-names";

/** Quem já ocupa nome e cor: os jogadores da sala ou os outros participantes do backtest. */
export type TakenSlot = Pick<RoomPlayer, "nickname" | "color">;

export type BotFormValues = {
  nickname: string;
  strategyKey: string;
  color: string;
  team: number | null;
  /** O rascunho de cada estratégia: trocar de estratégia e voltar mantém o que foi digitado */
  drafts: Record<string, ParamDraft>;
};

/** Um bot já existente, no formato que abre o formulário para editar. */
export type BotSource = {
  nickname: string;
  color: string;
  team?: number | null | undefined;
  strategyKey: string;
  params: ParamValues;
};

/** A primeira cor da paleta que ninguém tem. */
export function nextFreeColor(taken: Pick<TakenSlot, "color">[]) {
  return (PLAYER_COLORS.find((c) => !taken.some((p) => p.color === c.key)) ?? PLAYER_COLORS[0]).key;
}

const defaultDrafts = (strategies: StrategyInfo[]) =>
  Object.fromEntries(strategies.map((s) => [s.key, toDraft(defaultValues(s))]));

/** Os valores com que o formulário abre ao adicionar: 1ª estratégia, nome sorteado fora dos usados e a próxima cor livre. */
export function addValues(strategies: StrategyInfo[], taken: TakenSlot[], strategyKey?: string): BotFormValues {
  const strategy = strategies.find((s) => s.key === strategyKey) ?? strategies[0];
  return {
    nickname: strategy
      ? drawBotName(
          strategy,
          taken.map((p) => p.nickname),
        )
      : "",
    strategyKey: strategy?.key ?? "",
    color: nextFreeColor(taken),
    team: null,
    drafts: defaultDrafts(strategies),
  };
}

/** Os valores com que o formulário abre ao configurar um bot que já existe. */
export function editValues(strategies: StrategyInfo[], bot: BotSource): BotFormValues {
  const drafts = defaultDrafts(strategies);
  drafts[bot.strategyKey] = toDraft(bot.params);
  return { nickname: bot.nickname, strategyKey: bot.strategyKey, color: bot.color, team: bot.team ?? null, drafts };
}
