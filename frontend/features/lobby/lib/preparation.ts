import { defaultValues, profileValues, sameValues } from "@/shared/lib/strategy-params";
import type { Preparations, SavedStrategyParams, StrategyInfo, VoterValue } from "@/types";

/** Um partido que disputa eleitor com o do jogador: os do computador e os dos outros fundadores da sala. */
export type Rival = {
  abbr: string;
  name: string;
  /** Nulo no partido do computador, que tem a cor fixa da sigla */
  color: string | null;
  /** O fundador; nulo no partido do computador */
  founder: string | null;
  flags: VoterValue[];
};

export function rivalsOf(preparations: Preparations, nickname: string): Rival[] {
  const computer = preparations.reserved.map((party) => ({ ...party, color: null, founder: null }));
  const players = preparations.players.flatMap((player) =>
    player.kind === "FOUND" && player.party && player.nickname !== nickname
      ? [{ ...player.party, founder: player.nickname }]
      : [],
  );
  return [...computer, ...players];
}

/** As bandeiras do jogador que o rival também defende, na ordem das do jogador. */
export function sharedFlags(flags: VoterValue[], rival: Rival) {
  return flags.filter((flag) => rival.flags.includes(flag));
}

/** Quem disputa de perto: o rival com 2 ou mais bandeiras em comum marca cada uma delas ("MNV também"). */
export function closeRivalTag(flags: VoterValue[], rivals: Rival[]) {
  const close = rivals.filter((rival) => sharedFlags(flags, rival).length >= 2);
  return (flag: VoterValue) => {
    const abbrs = close.filter((rival) => flags.includes(flag) && rival.flags.includes(flag)).map((r) => r.abbr);
    return abbrs.length > 0 ? `${abbrs.join(", ")} também` : null;
  };
}

/** O partido em que o jogador está na preparação (o que fundou ou o do fundador em que entrou) e se ele encabeça a chapa. */
export function partyOf(preparations: Preparations, nickname: string) {
  const mine = preparations.players.find((player) => player.nickname === nickname);
  if (!mine || mine.kind === "NONE") return null;
  const owner = mine.kind === "FOUND" ? mine : preparations.players.find((player) => player.nickname === mine.founder);
  if (!owner?.party) return null;
  return { party: owner.party, founder: owner.nickname, candidate: owner.candidate === nickname };
}

/** Quanto a contribuição pesa no saldo inicial da sala, em porcentagem ("0,5%"). */
export function cashShare(amount: string, startingCash: string) {
  const cash = Number(startingCash);
  const share = cash > 0 ? (Number(amount) / cash) * 100 : 0;
  return `${share.toLocaleString("pt-BR", { maximumFractionDigits: 2 })}%`;
}

/** As estratégias cujos parâmetros salvos no perfil diferem do padrão. */
export function adjustedStrategies(strategies: StrategyInfo[], saved: SavedStrategyParams, tickers: string[]) {
  return new Set(
    strategies
      .filter((strategy) => {
        if (!saved[strategy.key]) return false;
        const { values } = profileValues(strategy, saved[strategy.key], tickers);
        return !sameValues(values, defaultValues(strategy));
      })
      .map((strategy) => strategy.key),
  );
}
