import { GAME_TYPES } from "@/shared/lib/game-types";
import type { ExpansionKey } from "@/shared/lib/expansions";
import type { GameType } from "@/types";

/** O tipo de partida que vale depois de desligar a expansão: o que depende dela volta a Clássica. */
export function gameTypeWithoutExpansion(gameType: GameType, expansion: ExpansionKey): GameType {
  return GAME_TYPES[gameType]?.expansion === expansion ? "CLASSIC" : gameType;
}
