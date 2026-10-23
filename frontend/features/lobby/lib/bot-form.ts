import { PLAYER_COLORS } from "@/shared/lib/player-colors";
import { defaultValues, toDraft, type ParamDraft } from "@/shared/lib/strategy-params";
import type { RoomBotRequest, RoomPlayer, StrategyInfo } from "@/types";
import { drawBotName } from "./bot-names";

/** O servidor recusa com 409 o nome que já está na sala. */
export const NAME_TAKEN_STATUS = 409;

/** O bot da sala como o pedido que o recria: nome, estratégia, parâmetros, cor e equipe. */
export function toBotRequest(player: RoomPlayer): RoomBotRequest | null {
  if (!player.bot) return null;
  return {
    nickname: player.nickname,
    strategy_key: player.bot.strategy_key,
    params: player.bot.params,
    color: player.color,
    team: player.team,
  };
}

export type BotFormValues = {
  nickname: string;
  strategyKey: string;
  color: string;
  team: number | null;
  /** O rascunho de cada estratégia: trocar de estratégia e voltar mantém o que foi digitado */
  drafts: Record<string, ParamDraft>;
};

/** A primeira cor da paleta que ninguém na sala tem. */
export function nextFreeColor(players: RoomPlayer[]) {
  return (PLAYER_COLORS.find((c) => !players.some((p) => p.color === c.key)) ?? PLAYER_COLORS[0]).key;
}

const defaultDrafts = (strategies: StrategyInfo[]) =>
  Object.fromEntries(strategies.map((s) => [s.key, toDraft(defaultValues(s))]));

/** Os valores com que o diálogo abre ao adicionar: 1ª estratégia, nome sorteado fora da sala e a próxima cor livre. */
export function addValues(strategies: StrategyInfo[], players: RoomPlayer[]): BotFormValues {
  const [first] = strategies;
  return {
    nickname: drawBotName(
      first,
      players.map((p) => p.nickname),
    ),
    strategyKey: first.key,
    color: nextFreeColor(players),
    team: null,
    drafts: defaultDrafts(strategies),
  };
}

/** Os valores com que o diálogo abre ao configurar um bot da sala. */
export function editValues(strategies: StrategyInfo[], player: RoomPlayer): BotFormValues {
  const drafts = defaultDrafts(strategies);
  const strategyKey = player.bot?.strategy_key ?? strategies[0].key;
  if (player.bot) drafts[strategyKey] = toDraft(player.bot.params);
  return { nickname: player.nickname, strategyKey, color: player.color, team: player.team ?? null, drafts };
}
