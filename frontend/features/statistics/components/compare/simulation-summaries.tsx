import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { cn } from "@/shared/lib/utils";
import { displayNumber, displaySignedPercent } from "@/shared/lib/utils/display";
import { VICTORY_CRITERIA } from "@/shared/lib/victory-criteria";
import type { OverviewReport, VictoryCriterion } from "@/types";
import { useStatisticsReport } from "../../hooks/queries/useStatisticsReport";
import { displayCriterionValue } from "../../lib/criterion";
import { SCORE_AXES } from "../../lib/metrics";
import { simulationColor, simulationLetter } from "../../lib/player-label";
import { SimulationLetter } from "./simulation-letter";

type Player = OverviewReport["players"][number];

const YOUR_CRITERION: Record<VictoryCriterion, string> = {
  SCORE: "Sua nota",
  RETURN: "Seu retorno",
  NETWORTH: "Seu patrimônio",
  SHARPE: "Seu Sharpe",
};

function Figure({ label, value, detail }: { label: string; value: string; detail?: string }) {
  return (
    <div className="grid gap-0.5">
      <span className="text-xs font-medium text-muted-foreground">{label}</span>
      <span className="font-mono text-lg font-semibold">{value}</span>
      {detail && <span className="text-xs text-muted-foreground">{detail}</span>}
    </div>
  );
}

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
        <CardDescription>vitória por {VICTORY_CRITERIA[data.criterion].label}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4">
          {you ? (
            <Figure
              label={YOUR_CRITERION[data.criterion]}
              value={displayCriterionValue(data.criterion, you.criterion_value)}
              detail={`${you.position}º lugar`}
            />
          ) : (
            <Figure label="Você" value="—" detail="não jogou esta partida" />
          )}
          {winner && (
            <Figure
              label="Vencedor"
              value={displayCriterionValue(data.criterion, winner.criterion_value)}
              detail={winner.player_nickname}
            />
          )}
          {you &&
            (data.criterion === "RETURN" ? (
              <Figure label="Sua nota" value={you.score ? displayNumber(you.score.total, 0) : "sem nota"} />
            ) : (
              <Figure label="Seu retorno" value={displaySignedPercent(you.return_percent)} />
            ))}
        </div>
      </CardContent>
    </Card>
  );
}

/** Os eixos da sua Nota em cada partida, com a diferença contra a primeira escolhida (A). */
function YouVersusYou({ simulationIds, currentPlayerName }: { simulationIds: number[]; currentPlayerName: string }) {
  const { data } = useStatisticsReport("overview", simulationIds, currentPlayerName);
  const scored = (data?.players ?? [])
    .filter((p) => p.score)
    .sort((a, b) => simulationIds.indexOf(a.simulation_id) - simulationIds.indexOf(b.simulation_id));
  if (scored.length < 2) return null;

  const pointsOf = (p: Player, axis: string) => p.score?.axes.find((a) => a.axis === axis)?.points ?? null;
  const base = scored[0];

  return (
    <Card className="overflow-hidden">
      <CardHeader>
        <CardTitle>Você contra você</CardTitle>
        <CardDescription>
          Seus eixos da Nota em cada partida. Cerca de 100 pontos num eixo é um bom desempenho; a diferença é contra a
          partida {simulationLetter(simulationIds, base.simulation_id)}.
        </CardDescription>
      </CardHeader>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Eixo</TableHead>
            {scored.map((p) => (
              <TableHead key={p.simulation_id} numeric>
                {simulationLetter(simulationIds, p.simulation_id)} · {p.simulation_name} ·{" "}
                {displayNumber(p.score!.total, 0)}
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {Object.entries(SCORE_AXES).map(([axis, info]) => (
            <TableRow key={axis}>
              <TableCell>{info.label}</TableCell>
              {scored.map((p, i) => {
                const value = pointsOf(p, axis);
                const reference = pointsOf(base, axis);
                const diff = i > 0 && value !== null && reference !== null ? Number(value) - Number(reference) : null;
                return (
                  <TableCell key={p.simulation_id} numeric>
                    <span className="inline-flex items-center gap-2">
                      {value === null ? "—" : displayNumber(value, 0)}
                      {diff !== null && diff !== 0 && (
                        <Badge variant={diff > 0 ? "success" : "destructive"} size="sm">
                          {diff > 0 ? "+" : "−"}
                          {displayNumber(Math.abs(diff), 0)}
                        </Badge>
                      )}
                    </span>
                  </TableCell>
                );
              })}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Card>
  );
}

interface SimulationSummariesProps {
  simulationIds: number[];
  currentPlayerName?: string;
}

/** O topo da comparação: um resumo por partida e, se você jogou mais de uma, você contra você. */
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
      {currentPlayerName && <YouVersusYou simulationIds={simulationIds} currentPlayerName={currentPlayerName} />}
    </>
  );
}
