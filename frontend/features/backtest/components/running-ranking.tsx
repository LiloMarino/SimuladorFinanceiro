import { TriangleAlert } from "lucide-react";
import { InfoHint } from "@/shared/components/info-hint";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import {
  displayIsoDate,
  displayMonthSlashYear,
  displayMoney,
  displaySignedPercent,
} from "@/shared/lib/utils/display";
import { cn } from "@/shared/lib/utils";
import type { BacktestPoint, BacktestFailure, BacktestParticipant, StrategyInfo } from "@/types";
import { referencesOf, standingsOf } from "../lib/standings";

type RunningRankingProps = {
  participants: BacktestParticipant[];
  strategies: StrategyInfo[];
  point: BacktestPoint | undefined;
  failures: BacktestFailure[];
};

const REFERENCE_NAMES = { cdi: "CDI", ibov: "Ibovespa" } as const;

/** A classificação de agora pelo patrimônio, com o retorno sobre o aportado; CDI e Ibovespa entram sem posição. */
export function RunningRanking({ participants, strategies, point, failures }: RunningRankingProps) {
  const standings = standingsOf(participants, point, failures);
  const references = referencesOf(point);
  const strategyName = (key: string) => strategies.find((s) => s.key === key)?.name ?? key;

  return (
    <Card>
      <CardHeader>
        <CardTitle>{point ? `Agora, em ${displayMonthSlashYear(point.day)}` : "Agora"}</CardTitle>
        <CardDescription>
          Pelo patrimônio de hoje e o retorno sobre o que foi aportado. A nota sai no fim.
        </CardDescription>
        <CardAction>
          <InfoHint label="O que é o retorno sobre o aportado">
            Mede quanto o patrimônio rendeu sobre todo o dinheiro que entrou (saldo inicial mais aportes). Exemplo: entrou
            R$ 150.000 e a carteira vale R$ 213.000, então o retorno é +42%. Acima de 0% a estratégia ganhou dinheiro;
            abaixo, a carteira vale menos do que foi posto. Compare com o CDI, que é o rendimento sem risco.
          </InfoHint>
        </CardAction>
      </CardHeader>
      <CardContent className="grid">
        {standings.length === 0 && <p className="text-sm text-muted-foreground">O primeiro ponto chega em instantes.</p>}
        {standings.map((standing, index) => {
          const { participant, failedOn } = standing;
          return (
            <div
              key={participant.nickname}
              className={cn(
                "grid grid-cols-[20px_28px_minmax(0,1fr)_auto] items-center gap-x-2.5 gap-y-0.5 border-t py-2.5 first:border-t-0",
                failedOn && "rounded-lg border-t-0 bg-destructive-soft px-2 py-2.25",
              )}
            >
              <span className="row-span-2 text-center font-mono text-xs text-faint-foreground">{index + 1}</span>
              <span className="row-span-2">
                <PlayerAvatar nickname={participant.nickname} color={participant.color} bot />
              </span>
              <span className="flex min-w-0 items-center gap-1.5 font-semibold">
                <span className="truncate" title={participant.nickname}>
                  {participant.nickname}
                </span>
                {failedOn && (
                  <Badge variant="destructive" size="tag">
                    <TriangleAlert />
                    parou
                  </Badge>
                )}
              </span>
              <span className="font-mono font-semibold">{displayMoney(standing.equity)}</span>
              <span
                className={cn(
                  "col-span-2 col-start-3 truncate text-xs",
                  failedOn ? "text-destructive" : "text-muted-foreground",
                )}
              >
                {failedOn
                  ? `Erro em ${displayIsoDate(failedOn)}: parou de operar e fica com a carteira que tinha.`
                  : `${strategyName(participant.strategy_key)} · ${displaySignedPercent(standing.returnOnContributed, 1)}`}
              </span>
            </div>
          );
        })}

        {/* Referências, sem posição */}
        {references.map((reference) => (
          <div
            key={reference.key}
            className="grid grid-cols-[20px_28px_minmax(0,1fr)_auto] items-center gap-x-2.5 gap-y-0.5 border-t py-2.5"
          >
            <span className="row-span-2" />
            <span className="row-span-2 flex justify-center" aria-hidden="true">
              <span
                className={cn(
                  "w-[18px] border-t-2",
                  reference.key === "cdi" ? "border-dashed border-foreground" : "border-dotted border-faint-foreground",
                )}
              />
            </span>
            <span className="font-semibold">{REFERENCE_NAMES[reference.key]}</span>
            <span className="font-mono font-semibold">{displayMoney(reference.equity)}</span>
            <span className="col-span-2 col-start-3 text-xs text-muted-foreground">
              referência · {displaySignedPercent(reference.returnOnContributed, 1)}
            </span>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
