import { stringToColor } from "@/shared/lib/utils";
import type { PlayerHistory } from "@/types";

export interface PlayerSeries {
  key: string;
  label: string;
  color: string;
  defaultVisible: boolean;
}

export function buildPlayerSeries(players: PlayerHistory[]): PlayerSeries[] {
  return players.map((p) => ({
    key: p.playerId,
    label: p.playerName,
    color: stringToColor(p.playerId),
    defaultVisible: true,
  }));
}
