import { drawBotName } from "@/shared/lib/bot-names";
import { defaultValues, type ParamValues } from "@/shared/lib/strategy-params";
import { RANDOM_STRATEGY } from "@/shared/lib/bot-form";
import type { Profession, RoomBotRequest, RoomPlayer, StrategyInfo } from "@/types";

/** O servidor recusa com 409 o nome que já está na sala. */
export const NAME_TAKEN_STATUS = 409;

type BatchChoice = { strategyKey: string; params: ParamValues; quantity: number; profession: Profession | null };

/**
 * Os pedidos de um lote de bots: cada um com o nome sorteado da lista da própria estratégia,
 * fora dos nomes da sala e dos já sorteados no lote. Uma profissão escolhida vale para o lote todo; sem ela
 * (nula), o servidor sorteia uma para cada bot. `RANDOM_STRATEGY` sorteia a estratégia
 * de cada bot, com os parâmetros padrão; uma estratégia escolhida leva os parâmetros do formulário.
 * Cor e equipe ficam por conta do servidor.
 */
export function batchRequests(
  strategies: StrategyInfo[],
  takenNames: string[],
  { strategyKey, params, quantity, profession }: BatchChoice,
  random: () => number = Math.random,
): RoomBotRequest[] {
  const taken = [...takenNames];
  const requests: RoomBotRequest[] = [];
  for (let i = 0; i < quantity; i++) {
    const strategy =
      strategyKey === RANDOM_STRATEGY
        ? strategies[Math.floor(random() * strategies.length)]
        : strategies.find((s) => s.key === strategyKey);
    if (!strategy) break;

    const nickname = drawBotName(strategy, taken, random);
    taken.push(nickname);
    requests.push({
      nickname,
      strategy_key: strategy.key,
      params: strategyKey === RANDOM_STRATEGY ? defaultValues(strategy) : params,
      profession,
    });
  }
  return requests;
}

/** O bot da sala como o pedido que o recria: nome, estratégia, parâmetros, cor e equipe. */
export function toBotRequest(player: RoomPlayer): RoomBotRequest | null {
  if (!player.bot) return null;
  return {
    nickname: player.nickname,
    strategy_key: player.bot.strategy_key,
    params: player.bot.params,
    color: player.color,
    team: player.team,
    profession: player.profession,
  };
}
