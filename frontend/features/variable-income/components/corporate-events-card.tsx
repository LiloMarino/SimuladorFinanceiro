import { Fragment, useState } from "react";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableEmptyRow,
  TableHead,
  TableHeader,
  TableRow,
} from "@/shared/components/ui/table";
import { ErrorState } from "@/shared/components/error-state";
import { MetricHint } from "@/shared/components/metric-hint";
import { DIVIDEND_YIELD } from "@/shared/lib/dividend-metrics";
import { describeSplit } from "@/shared/lib/split-ratio";
import { cn } from "@/shared/lib/utils";
import {
  displayIsoDate,
  displayMoney,
  displayPercent,
  displayQuantity,
  displayShortDate,
} from "@/shared/lib/utils/display";
import type { AssetCorporateEvent, AssetCorporateEvents } from "@/types";
import { useCorporateEvents } from "../hooks/queries/useCorporateEvents";

/** Quantos eventos aparecem antes do "Mostrar mais". */
const VISIBLE_EVENTS = 6;

/** Histórico de proventos, desdobramentos e grupamentos do ativo, até o dia de hoje da partida. */
export function CorporateEventsCard({ ticker }: { ticker: string }) {
  const { data, isLoading, error, refetch } = useCorporateEvents(ticker);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Proventos e eventos</CardTitle>
        <CardDescription>
          O provento cai no seu caixa na data ex, pela quantidade que você tinha na abertura do dia. Desdobramentos e
          grupamentos mudam só a quantidade de ações: o valor da posição continua o mesmo.
        </CardDescription>
        {data && (
          <CardAction>
            <CorporateEventsKpis data={data} />
          </CardAction>
        )}
      </CardHeader>
      <CardContent>
        {isLoading && <Skeleton className="h-40" />}
        {!isLoading && !data && (
          <ErrorState
            title="Não deu pra carregar o histórico"
            description="Os proventos já recebidos continuam no caixa. Tente de novo."
            error={error}
            onRetry={() => void refetch()}
          />
        )}
        {data && <CorporateEventsBody data={data} />}
      </CardContent>
    </Card>
  );
}

function CorporateEventsBody({ data }: { data: AssetCorporateEvents }) {
  const [showAll, setShowAll] = useState(false);
  const hidden = showAll ? 0 : Math.max(0, data.events.length - VISIBLE_EVENTS);
  const events = showAll ? data.events : data.events.slice(0, VISIBLE_EVENTS);
  const firstBefore = events.findIndex((event) => event.before_match);

  return (
    <div className="grid gap-5">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Data ex</TableHead>
            <TableHead>Evento</TableHead>
            <TableHead numeric>Por ação</TableHead>
            <TableHead numeric>Suas ações no dia</TableHead>
            <TableHead numeric>Você recebeu</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {events.length === 0 && (
            <TableEmptyRow colSpan={5}>
              <span className="text-muted-foreground">Nenhum provento ou desdobramento até hoje.</span>
            </TableEmptyRow>
          )}
          {events.map((event, index) => (
            <Fragment key={`${event.kind}-${event.ex_date}`}>
              {index === firstBefore && <MatchStartRow date={data.match_start_date} />}
              <EventRow event={event} />
            </Fragment>
          ))}
        </TableBody>
      </Table>

      {hidden > 0 && (
        <Button variant="ghost" size="sm" className="justify-self-center" onClick={() => setShowAll(true)}>
          Mostrar mais {hidden} {hidden === 1 ? "evento anterior" : "eventos anteriores"}
        </Button>
      )}
    </div>
  );
}

/** DY de 12 meses e o total recebido no ativo, à direita do cabeçalho. */
function CorporateEventsKpis({ data }: { data: AssetCorporateEvents }) {
  return (
    <div className="flex gap-6">
      <div className="grid justify-items-end gap-0.5 text-right">
        <span className="inline-flex items-center gap-1 text-xs font-medium text-muted-foreground">
          {DIVIDEND_YIELD.label}
          <MetricHint metric={DIVIDEND_YIELD} />
        </span>
        <b className="font-mono text-lg">
          {data.dividend_yield_12m === null ? "—" : displayPercent(data.dividend_yield_12m)}
        </b>
        <span className="text-xs text-faint-foreground">
          {data.dividend_yield_12m === null
            ? "Este ativo não paga provento."
            : `${displayMoney(data.per_share_12m)} por ação em 12 meses`}
        </span>
      </div>
      <div className="grid gap-0.5 border-l pl-6 text-right">
        <span className="text-xs font-medium text-muted-foreground">Você recebeu</span>
        <b className="font-mono text-lg">{displayMoney(data.received_total)}</b>
        <span className="text-xs text-faint-foreground">
          em {data.payments_count} {data.payments_count === 1 ? "provento" : "proventos"} na partida
        </span>
      </div>
    </div>
  );
}

/** Separa o que aconteceu depois do início da partida do que veio antes dele. */
function MatchStartRow({ date }: { date: string }) {
  return (
    <TableRow variant="subtle">
      <TableCell variant="note" colSpan={5}>
        Início da partida · {displayIsoDate(date)} · antes disso, você não tinha como receber
      </TableCell>
    </TableRow>
  );
}

function EventRow({ event }: { event: AssetCorporateEvent }) {
  // Antes do início da partida o jogador não tinha posição: os valores ficam esmaecidos
  const dim = event.before_match ? "text-muted-foreground" : undefined;
  const isDividend = event.kind === "DIVIDEND";
  const split = isDividend ? null : describeSplit(event.value);
  const shares =
    event.shares === null
      ? "—"
      : event.shares_after === null
        ? displayQuantity(event.shares)
        : `${displayQuantity(event.shares)} → ${displayQuantity(event.shares_after)}`;

  return (
    <TableRow>
      <TableCell>
        <span className={dim}>{displayShortDate(event.ex_date)}</span>
      </TableCell>
      <TableCell>
        {split === null ? (
          <Badge variant="dividend">Provento</Badge>
        ) : (
          <span className="flex items-center gap-2">
            <Badge variant="split">{split.name}</Badge>
            <span className={cn("font-mono text-xs", dim)}>{split.label}</span>
          </span>
        )}
      </TableCell>
      <TableCell numeric>
        <span className={dim}>{isDividend ? displayMoney(event.value) : "—"}</span>
      </TableCell>
      <TableCell numeric>
        <span className={dim}>{shares}</span>
      </TableCell>
      <TableCell numeric>
        <span className={dim}>{event.received === null ? "—" : displayMoney(event.received)}</span>
      </TableCell>
    </TableRow>
  );
}
