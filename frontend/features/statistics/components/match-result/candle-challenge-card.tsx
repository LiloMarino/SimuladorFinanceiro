import { ChartCandlestick } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { useCandleChallengeRanking } from "../../hooks/queries/useCandleChallengeRanking";

type CandleChallengeCardProps = {
  simulationId: number;
  currentPlayerName: string | undefined;
};

/** O placar do desafio da vela: acertos em "sobe ou desce?", fora da nota e do ranking. */
export function CandleChallengeCard({ simulationId, currentPlayerName }: CandleChallengeCardProps) {
  const { data: ranking, isPending, isError, refetch } = useCandleChallengeRanking([simulationId]);

  return (
    <Card size="sm">
      <CardHeader>
        <CardTitle>
          <span className="flex items-center gap-2">
            <ChartCandlestick className="size-4 text-muted-foreground" />
            Desafio da vela
          </span>
        </CardTitle>
        <CardDescription>Acertos em “sobe ou desce?”. Não entra na nota nem no ranking.</CardDescription>
      </CardHeader>
      <CardContent>
        {isPending && <Skeleton className="h-24" />}
        {isError && (
          <div className="grid justify-items-start gap-2 text-xs text-muted-foreground">
            Não deu para carregar o placar do desafio.
            <Button variant="outline" size="sm" onClick={() => void refetch()}>
              Tentar de novo
            </Button>
          </div>
        )}
        {ranking && ranking.players.length === 0 && (
          <p className="text-xs text-muted-foreground">
            Ninguém respondeu nesta partida. Ele aparece no gráfico de velas quando surge um padrão.
          </p>
        )}
        {ranking && ranking.players.length > 0 && (
          <ol className="grid">
            {ranking.players.map((player) => (
              <li
                key={player.player_nickname}
                className="grid grid-cols-[24px_minmax(0,1fr)_auto] items-center gap-2 py-1 text-[13px]"
              >
                <span className="font-mono text-muted-foreground">{player.position}º</span>
                <span className="truncate">
                  {player.player_nickname === currentPlayerName ? "Você" : player.player_nickname}
                </span>
                <span className="font-mono">
                  {player.hits} de {player.answered}
                </span>
              </li>
            ))}
          </ol>
        )}
      </CardContent>
    </Card>
  );
}
