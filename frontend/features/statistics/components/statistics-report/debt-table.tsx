import { MetricHint } from "@/shared/components/metric-hint";
import { SortableTableHead } from "@/shared/components/sortable-table-head";
import { Card, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Table, TableBody, TableCell, TableHeader, TableRow } from "@/shared/components/ui/table";
import { useTableSort } from "@/shared/hooks/useTableSort";
import { LEVERAGE, RISK_RATING } from "@/shared/lib/credit-metrics";
import { sortNumber } from "@/shared/lib/table-sort";
import { displayMoney } from "@/shared/lib/utils/display";
import type { RiskPlayer } from "@/types";
import { playerKey, playerLabel } from "../../lib/player-label";
import { PlayerCell } from "./shared";

type DebtTableProps = {
  players: RiskPlayer[];
  simulationIds: number[];
  currentPlayerName: string | undefined;
};

// Nota na ordem da escada, da melhor para a pior, para a coluna ordenar pela qualidade
const GRADE_RANK: Record<RiskPlayer["credit_grade"], number> = {
  AAA: 0,
  AA: 1,
  A: 2,
  BBB: 3,
  BB: 4,
  B: 5,
  CCC: 6,
  D: 7,
};

/** "Dívida na sala": quanto cada jogador deve, quanto isso pesa no patrimônio e a nota que isso rende. */
export function DebtTable({ players, simulationIds, currentPlayerName }: DebtTableProps) {
  const sorting = useTableSort(players, {
    player: (p) => playerLabel(p, simulationIds, currentPlayerName),
    debt: (p) => sortNumber(p.debt),
    leverage: (p) => sortNumber(p.leverage),
    grade: (p) => GRADE_RANK[p.credit_grade],
  });

  return (
    <Card className="overflow-hidden">
      <CardHeader>
        <CardTitle>Dívida na sala</CardTitle>
        <CardDescription>Quem está pegando dinheiro emprestado, e quanto</CardDescription>
      </CardHeader>
      <Table>
        <TableHeader>
          <TableRow>
            <SortableTableHead label="Jogador" {...sorting.header("player")} />
            <SortableTableHead label="Dívida" {...sorting.header("debt")} numeric />
            <SortableTableHead
              label={LEVERAGE.label}
              {...sorting.header("leverage")}
              numeric
              hint={<MetricHint metric={LEVERAGE} />}
            />
            <SortableTableHead
              label={RISK_RATING.label}
              {...sorting.header("grade")}
              numeric
              hint={<MetricHint metric={RISK_RATING} />}
            />
          </TableRow>
        </TableHeader>
        <TableBody>
          {sorting.rows.map((p) => {
            const label = playerLabel(p, simulationIds, currentPlayerName);
            return (
              <TableRow key={playerKey(p)} variant={p.player_nickname === currentPlayerName ? "current" : "default"}>
                <TableCell>
                  <PlayerCell
                    player={p}
                    label={label}
                    simulationIds={simulationIds}
                    isYou={p.player_nickname === currentPlayerName}
                  />
                </TableCell>
                <TableCell numeric>{Number(p.debt) > 0 ? displayMoney(p.debt) : "—"}</TableCell>
                <TableCell numeric>{p.leverage === null ? "—" : LEVERAGE.format(p.leverage)}</TableCell>
                <TableCell numeric>{p.credit_grade}</TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </Card>
  );
}
