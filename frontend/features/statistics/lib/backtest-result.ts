import type { BacktestParticipant, BacktestResult, Player } from "@/types";

export type BacktestMeasure = "SCORE" | "RETURN" | "NETWORTH";

export type BacktestRow = {
  player: Player;
  participant: BacktestParticipant;
  score: number | null;
  networth: number;
  /** Retorno sobre o que foi aportado (0,42 = +42%) */
  returnOnContributed: number;
  /** Retorno da estratégia menos o do CDI, em fração (0,25 = 25 p.p.) */
  overCdi: number;
  /** O dia do erro que fez a estratégia parar de operar */
  failedOn: string | null;
};

type BacktestReference = {
  networth: number;
  returnOnContributed: number;
};

export type BacktestReferences = {
  contributed: number;
  cdi: BacktestReference;
  /** Nulo quando o período não tem dado do Ibovespa */
  ibov: BacktestReference | null;
};

const returnOn = (networth: number, contributed: number) => (contributed > 0 ? networth / contributed - 1 : 0);

/** CDI e Ibovespa no último pregão rodado, como carteiras que receberam os mesmos aportes. */
export function finalReferences(result: BacktestResult): BacktestReferences | null {
  const last = result.references.at(-1);
  if (!last) return null;
  const contributed = Number(last.contributed);
  const reference = (value: string): BacktestReference => ({
    networth: Number(value),
    returnOnContributed: returnOn(Number(value), contributed),
  });
  return { contributed, cdi: reference(last.cdi), ibov: last.ibov === null ? null : reference(last.ibov) };
}

/** Une o ranking do relatório à configuração do backtest; só entra quem é participante dele. */
export function backtestRows(players: Player[], result: BacktestResult, references: BacktestReferences): BacktestRow[] {
  return result.config.participants.flatMap((participant) => {
    const player = players.find((p) => p.player_nickname === participant.nickname);
    if (!player) return [];
    const networth = Number(player.total_networth);
    const returnOnContributed = returnOn(networth, references.contributed);
    return [
      {
        player,
        participant,
        score: player.score ? Number(player.score.total) : null,
        networth,
        returnOnContributed,
        overCdi: returnOnContributed - references.cdi.returnOnContributed,
        failedOn: result.failures.find((f) => f.nickname === participant.nickname)?.day ?? null,
      },
    ];
  });
}

const MEASURE_VALUE: Record<BacktestMeasure, (row: BacktestRow) => number | null> = {
  SCORE: (row) => row.score,
  RETURN: (row) => row.returnOnContributed,
  NETWORTH: (row) => row.networth,
};

/** Da maior para a menor pela medida; quem não tem o valor (sem nota) fica no fim. */
export function rankRows(rows: BacktestRow[], measure: BacktestMeasure): BacktestRow[] {
  const valueOf = MEASURE_VALUE[measure];
  return [...rows].sort((a, b) => (valueOf(b) ?? -Infinity) - (valueOf(a) ?? -Infinity));
}

/** A nota vale quando alguém a tem; antes de 63 pregões a classificação cai para o patrimônio. */
export function defaultMeasure(rows: BacktestRow[]): BacktestMeasure {
  return rows.some((row) => row.score !== null) ? "SCORE" : "NETWORTH";
}
