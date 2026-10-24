import type { RoomBotRequest, RoomPlayer } from "@/types";

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
