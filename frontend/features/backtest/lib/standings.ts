import type { BacktestFailure, BacktestParticipant, BacktestPoint } from "@/types";

export type Standing = {
  participant: BacktestParticipant;
  equity: number;
  /** Retorno sobre o que foi aportado até o dia (0,42 = +42%) */
  returnOnContributed: number;
  /** O dia do erro que fez a estratégia parar de operar */
  failedOn: string | null;
};

export type ReferenceStanding = {
  key: "cdi" | "ibov";
  equity: number;
  returnOnContributed: number;
};

const returnOn = (equity: number, contributed: number) => (contributed > 0 ? equity / contributed - 1 : 0);

/** A classificação no último ponto: pelo patrimônio, da maior para a menor carteira. */
export function standingsOf(
  participants: BacktestParticipant[],
  point: BacktestPoint | undefined,
  failures: BacktestFailure[],
): Standing[] {
  if (!point) return [];
  const contributed = Number(point.contributed);
  return participants
    .map((participant, index) => {
      const equity = Number(point.equity[index]);
      return {
        participant,
        equity,
        returnOnContributed: returnOn(equity, contributed),
        failedOn: failures.find((f) => f.nickname === participant.nickname)?.day ?? null,
      };
    })
    .sort((a, b) => b.equity - a.equity);
}

/** CDI e Ibovespa como carteiras que receberam os mesmos aportes; o Ibovespa some enquanto não tem dado. */
export function referencesOf(point: BacktestPoint | undefined): ReferenceStanding[] {
  if (!point) return [];
  const contributed = Number(point.contributed);
  const cdi = Number(point.cdi);
  const references: ReferenceStanding[] = [{ key: "cdi", equity: cdi, returnOnContributed: returnOn(cdi, contributed) }];
  if (point.ibov !== null) {
    const ibov = Number(point.ibov);
    references.push({ key: "ibov", equity: ibov, returnOnContributed: returnOn(ibov, contributed) });
  }
  return references;
}
