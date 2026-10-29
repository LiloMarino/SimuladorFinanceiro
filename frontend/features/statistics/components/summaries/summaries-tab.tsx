import { useState } from "react";
import { CalendarRange, ChevronDown, FileText } from "lucide-react";
import { ErrorState } from "@/shared/components/error-state";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from "@/shared/components/ui/empty";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { cn } from "@/shared/lib/utils";
import { displayIsoDate, displaySignedPercent } from "@/shared/lib/utils/display";
import type { Summary } from "@/types";
import { useSummaries } from "../../hooks/queries/useSummaries";
import { summaryTitle } from "../../lib/summary";
import { MonthSummaryView } from "./month-summary";
import { YearReviewView } from "./year-review";

type SummariesTabProps = { simulationId: number };

/** Os resumos do mês e as retrospectivas do ano que o jogador recebeu na partida, abertos um por vez. */
export function SummariesTab({ simulationId }: SummariesTabProps) {
  const { data: summaries, isPending, error, refetch } = useSummaries(simulationId);
  const [expanded, setExpanded] = useState<Summary["id"] | null>(null);

  if (isPending) {
    return (
      <Card>
        <CardContent>
          <div className="grid gap-2">
            <Skeleton className="h-12" />
            <Skeleton className="h-12" />
            <Skeleton className="h-12" />
          </div>
        </CardContent>
      </Card>
    );
  }
  if (!summaries) {
    return (
      <ErrorState
        title="Não deu para carregar os resumos"
        description="A partida segue normal. Tente de novo em instantes."
        error={error}
        onRetry={() => void refetch()}
      />
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Resumos</CardTitle>
        <CardDescription>
          O resumo de cada mês chega na virada do mês, e a retrospectiva do ano na virada do ano.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid content-start gap-2">
          {summaries.length === 0 ? (
            <Empty>
              <EmptyHeader>
                <EmptyMedia variant="icon">
                  <FileText />
                </EmptyMedia>
                <EmptyTitle>Nada por aqui ainda</EmptyTitle>
                <EmptyDescription>O resumo do primeiro mês chega no primeiro pregão do mês seguinte.</EmptyDescription>
              </EmptyHeader>
            </Empty>
          ) : (
            summaries.map((summary) => (
              <SummaryRow
                key={summary.id}
                summary={summary}
                open={summary.id === expanded}
                onToggle={() => setExpanded(summary.id === expanded ? null : summary.id)}
              />
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}

type SummaryRowProps = {
  summary: Summary;
  open: boolean;
  onToggle: () => void;
};

function SummaryRow({ summary, open, onToggle }: SummaryRowProps) {
  const content = summary.content;
  const Icon = content.kind === "YEAR_REVIEW" ? CalendarRange : FileText;
  const result = content.return_pct === null ? null : Number(content.return_pct);

  return (
    <article className="rounded-lg border border-border bg-card">
      <button
        type="button"
        aria-expanded={open}
        className="flex w-full items-center gap-3 px-3.5 py-3 text-left"
        onClick={onToggle}
      >
        <Icon className="size-4 shrink-0 text-muted-foreground" />
        <span className="grid min-w-0 flex-1">
          <span className="truncate text-sm font-medium">{summaryTitle(content)}</span>
          <span className="text-xs text-muted-foreground">{displayIsoDate(summary.game_date)}</span>
        </span>
        {content.return_pct !== null && (
          <span
            className={cn(
              "font-mono text-[13px] font-semibold tabular-nums",
              result !== null && result > 0 && "text-success",
              result !== null && result < 0 && "text-destructive",
            )}
          >
            {displaySignedPercent(content.return_pct)}
          </span>
        )}
        <ChevronDown
          className={cn("size-4 shrink-0 text-muted-foreground transition-transform", open && "rotate-180")}
        />
      </button>
      {open && (
        <div className="border-t border-border px-3.5 py-3">
          {content.kind === "YEAR_REVIEW" ? (
            <YearReviewView review={content} />
          ) : (
            <MonthSummaryView summary={content} />
          )}
        </div>
      )}
    </article>
  );
}
