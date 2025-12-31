import { Card, CardContent } from "@/shared/components/ui/card";

interface MatchSummary {
  position: number;
  playerReturn: string;
  averageReturn: string;
  bestReturn: string;
  worstReturn: string;
}

interface Props {
  summary: MatchSummary;
}

export function MatchSummaryCard({ summary }: Props) {
  return (
    <Card>
      <CardContent className="space-y-4 pt-1 pb-2">
        {/* Título discreto */}
        <p className="font-medium text-muted-foreground text-center">Resumo da Partida</p>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-center">
          <SummaryItem label="Sua posição" value={`${summary.position}º`} />
          <SummaryItem label="Seu retorno" value={summary.playerReturn} />
          <SummaryItem label="Média da sala" value={summary.averageReturn} />
          <SummaryItem label="Melhor retorno" value={summary.bestReturn} />
          <SummaryItem label="Pior retorno" value={summary.worstReturn} />
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
