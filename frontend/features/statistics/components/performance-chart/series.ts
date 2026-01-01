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
    key: p.player_nickname,
    label: p.player_nickname,
    color: stringToColor(p.player_nickname),
    defaultVisible: true,
  }));
}
