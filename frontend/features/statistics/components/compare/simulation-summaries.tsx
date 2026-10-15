import { Badge } from "@/shared/components/ui/badge";
import { Card, CardAction, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { cn } from "@/shared/lib/utils";
import { displayNumber, displaySignedPercent } from "@/shared/lib/utils/display";
import { VICTORY_CRITERIA } from "@/shared/lib/victory-criteria";
import type { OverviewReport, VictoryCriterion } from "@/types";
import { useStatisticsReport } from "../../hooks/queries/useStatisticsReport";
import { displayCriterionValue } from "../../lib/criterion";
import { simulationColor, simulationLetter } from "../../lib/player-label";
import { SimulationLetter } from "./simulation-letter";

type Player = OverviewReport["players"][number];

const YOUR_CRITERION: Record<VictoryCriterion, string> = {
  SCORE: "Sua nota",
  RETURN: "Seu retorno",
  NETWORTH: "Seu patrimônio",
  SHARPE: "Seu Sharpe",
};

function Figure({
  label,
  value,
  detail,
  tone,
}: {
  label: string;
  value: string;
  detail?: string;
  tone?: "negative";
}) {
  return (
    <div className="grid gap-0.5">
      <span className="text-xs font-medium text-muted-foreground">{label}</span>
      <span className={cn("font-mono text-lg font-semibold", tone === "negative" && "text-destructive")}>{value}</span>
      {detail && <span className="text-xs text-muted-foreground">{detail}</span>}
    </div>
  );
}

// O valor no critério sem a unidade "pts": a coluna já diz o que é
const withoutUnit = (value: string) => value.replace(/ pts$/, "");

interface SummaryProps {
  simulationIds: number[];
  simulationId: number;
  currentPlayerName?: string;
}

/** Uma partida escolhida: o critério dela, onde você ficou e quem venceu. */
function SimulationSummary({ simulationIds, simulationId, currentPlayerName }: SummaryProps) {
  const { data } = useStatisticsReport("overview", [simulationId]);
  if (!data) return <Skeleton className="h-36" />;

  const winner = data.players[0] as Player | undefined;
  const you = data.players.find((p) => p.player_nickname === currentPlayerName);
  const name = winner?.simulation_name ?? "Sem jogadores";

  return (
    // Faixa de 3 px na cor da partida, a mesma da letra
    <div className="rounded-xl border-t-[3px]" style={{ borderTopColor: simulationColor(simulationIds, simulationId) }}>
      <Card size="sm">
        <CardHeader>
          <CardTitle>
            <span className="flex items-center gap-2">
              <SimulationLetter
                letter={simulationLetter(simulationIds, simulationId)}
                color={simulationColor(simulationIds, simulationId)}
              />
              {name}
            </span>
          </CardTitle>
          <CardAction>
            <Badge variant="secondary">vitória por {VICTORY_CRITERIA[data.criterion].label}</Badge>
          </CardAction>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4">
            {you ? (
              <Figure
                label={YOUR_CRITERION[data.criterion]}
                value={withoutUnit(displayCriterionValue(data.criterion, you.criterion_value))}
                detail={`${you.position}º lugar`}
              />
            ) : (
              <Figure label="Você" value="—" detail="não jogou esta partida" />
            )}
            {winner && (
              <Figure
                label="Vencedor"
                value={withoutUnit(displayCriterionValue(data.criterion, winner.criterion_value))}
                detail={winner.player_nickname}
              />
            )}
            {you &&
              (data.criterion === "RETURN" ? (
                <Figure label="Sua nota" value={you.score ? displayNumber(you.score.total, 0) : "sem nota"} />
              ) : (
                <Figure
                  label="Seu retorno"
                  value={displaySignedPercent(you.return_percent)}
                  tone={Number(you.return_percent) < 0 ? "negative" : undefined}
                />
              ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

interface SimulationSummariesProps {
  simulationIds: number[];
  currentPlayerName?: string;
}

/** O topo da comparação: um resumo por partida. O "você contra você" fecha a aba Geral. */
export function SimulationSummaries({ simulationIds, currentPlayerName }: SimulationSummariesProps) {
  return (
    <>
      <div
        className={cn(
          "grid gap-4",
          simulationIds.length > 1 && "md:grid-cols-2",
          simulationIds.length > 2 && "xl:grid-cols-3",
        )}
      >
        {simulationIds.map((id) => (
          <SimulationSummary
            key={id}
            simulationIds={simulationIds}
            simulationId={id}
            currentPlayerName={currentPlayerName}
          />
        ))}
      </div>
    </>
  );
}
