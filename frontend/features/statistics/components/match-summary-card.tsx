import { Card, CardContent } from "@/shared/components/ui/card";
import { displayPercent } from "@/shared/lib/utils/display";
import type { PerformanceReport } from "@/types";

interface Props {
  report: PerformanceReport;
  currentPlayerName: string;
}

export function MatchSummaryCard({ report, currentPlayerName }: Props) {
  const { players, average_return } = report;
  const current = players.find((p) => p.player_nickname === currentPlayerName);

  // O ranking chega ordenado do melhor para o pior retorno
  const best = players[0];
  const worst = players[players.length - 1];

  return (
    <Card>
      <CardContent className="space-y-4 pt-1 pb-2">
        {/* Título discreto */}
        <p className="font-medium text-muted-foreground text-center">Resumo da Partida</p>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-center">
          <SummaryItem label="Sua posição" value={current ? `${current.position}º` : "—"} />
          <SummaryItem label="Seu retorno" value={current ? displayPercent(current.return_percent) : "—"} />
          <SummaryItem label="Média da sala" value={average_return ? displayPercent(average_return) : "—"} />
          <SummaryItem label="Melhor retorno" value={displayPercent(best.return_percent)} />
          <SummaryItem label="Pior retorno" value={displayPercent(worst.return_percent)} />
        </div>
      </CardContent>
    </Card>
  );
}

function SummaryItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="space-y-1">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="text-lg font-semibold">{value}</p>
    </div>
  );
}
