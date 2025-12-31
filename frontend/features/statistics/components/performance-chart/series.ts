import { stringToColor } from "@/shared/lib/utils";

export interface PlayerSeries {
  key: string;
  label: string;
  color: string;
  defaultVisible: boolean;
}

export function buildPlayerSeries(players: { playerId: string; playerName: string }[]): PlayerSeries[] {
  return players.map((p) => ({
    key: p.playerId,
    label: p.playerName,
    color: stringToColor(p.playerId),
    defaultVisible: true,
  }));
}
