import { useState } from "react";
import { Info } from "lucide-react";
import { MetricHint } from "@/shared/components/metric-hint";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { cn } from "@/shared/lib/utils";
import { displayDayMonth } from "@/shared/lib/utils/display";
import type { TermPromises } from "@/types";
import { useBalances } from "../hooks/queries/useBalances";
import { AFFINITY, REJECTION } from "../lib/election-metrics";
import { PROMISE_STATE, promiseValue, stateLabel, stateSummary } from "../lib/promises";
import { GROUP_INFO } from "../lib/voters";
import { BalanceDialog } from "./balance-dialog";
import { SignedDecimal } from "./signed-decimal";
import { GroupIcon } from "./value-chip";

type TermPromisesCardProps = { promises: TermPromises; termEnd: string | null };

type Item = TermPromises["items"][number];

/** O que a medida vale hoje no país: a alíquota, o teto da isenção, ou o setor isento ou não. */
function currentLabel(item: Item) {
  if (item.current === null) return item.state === "FULFILLED" ? "isento" : "ainda não é isento";
  return promiseValue(item.promise.kind, item.current);
}

/** As promessas da chapa que governa: o estado de cada uma hoje e, para os filiados, o que o mandato deixaria no partido. */
export function TermPromisesCard({ promises, termEnd }: TermPromisesCardProps) {
  const [balanceOpen, setBalanceOpen] = useState(false);
  const balances = useBalances(true);
  const hasBalance = (balances.data?.length ?? 0) > 0;

  return (
    <Card>
      <CardContent>
        <div className="grid gap-4">
          {/* Cabeçalho */}
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div className="grid gap-1">
              <div className="flex flex-wrap items-center gap-2.5">
                <h2 className="text-[15px] font-semibold">Promessas da chapa do {promises.party_abbr}</h2>
                <Badge variant="secondary" size="sm">
                  {stateSummary(promises.items)}
                </Badge>
              </div>
              <span className="text-[13px] text-muted-foreground">
                Cobradas no fim do mandato pelo que estiver em vigor
                {termEnd ? ` em ${displayDayMonth(termEnd)}` : ""}. A sala vê o estado de cada uma.
              </span>
            </div>
            {hasBalance && (
              <Button size="sm" variant="outline" onClick={() => setBalanceOpen(true)}>
                Ver o balanço do último mandato
              </Button>
            )}
          </div>

          {promises.last_vote && (
            <Alert variant="info">
              <Info />
              <AlertTitle>A votação de {displayDayMonth(promises.last_vote)} é a última que conta</AlertTitle>
              <AlertDescription>
                Medida aprovada depois dela só passa a valer depois do fim do mandato.
              </AlertDescription>
            </Alert>
          )}

          {/* Promessas */}
          <div
            className={cn(
              "grid gap-px overflow-hidden rounded-lg border bg-border",
              promises.items.length >= 3 ? "md:grid-cols-3" : promises.items.length === 2 && "md:grid-cols-2",
            )}
          >
            {promises.items.map((item) => (
              <div key={item.promise.title} className="grid content-start gap-1.5 bg-card p-3.5">
                <div className="flex items-start justify-between gap-2">
                  <b className="min-w-0 text-[13px]" title={item.promise.title}>
                    {item.promise.title}
                  </b>
                  <Badge variant={PROMISE_STATE[item.state].variant} size="sm">
                    {stateLabel(item.state, item.done)}
                  </Badge>
                </div>
                <span className="font-mono text-xs">
                  hoje {currentLabel(item)}
                  {item.promise.target !== null && ` · alvo ${promiseValue(item.promise.kind, item.promise.target)}`}
                </span>
                <span className="text-xs text-muted-foreground">
                  {item.promise.baseline !== null
                    ? `Era ${promiseValue(item.promise.kind, item.promise.baseline)} no anúncio, em ${displayDayMonth(item.promise.announced)}.`
                    : `Anunciada em ${displayDayMonth(item.promise.announced)}.`}
                </span>
                {item.state === "CONTRARY" && (
                  <span className="text-xs text-destructive">
                    Se terminar assim, a rejeição sai 1,5 vez a de não ter feito nada.
                  </span>
                )}
              </div>
            ))}
          </div>

          {/* Se o mandato acabasse hoje, só para os filiados */}
          {promises.projection.length > 0 && (
            <div className="grid gap-2">
              <b className="text-sm">Se o mandato acabasse hoje</b>
              <span className="text-xs text-muted-foreground">
                {promises.items.length === 1
                  ? "O que a promessa deixaria"
                  : `O que as ${promises.items.length} promessas deixariam`}{" "}
                no {promises.party_abbr}. Só o {promises.party_abbr} vê.
              </span>
              <div className="overflow-hidden rounded-lg border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Grupo</TableHead>
                      <TableHead numeric>
                        <span className="inline-flex items-center gap-1">
                          {AFFINITY.label}
                          <MetricHint metric={AFFINITY} />
                        </span>
                      </TableHead>
                      <TableHead numeric>
                        <span className="inline-flex items-center gap-1">
                          {REJECTION.label}
                          <MetricHint metric={REJECTION} />
                        </span>
                      </TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {promises.projection.map((row) => (
                      <TableRow key={row.group}>
                        <TableCell>
                          <span className="flex items-center gap-2.5">
                            <GroupIcon group={row.group} className="size-7" />
                            {GROUP_INFO[row.group].label}
                          </span>
                        </TableCell>
                        <TableCell numeric>
                          <SignedDecimal value={row.loyalty} rising="good" />
                        </TableCell>
                        <TableCell numeric>
                          <SignedDecimal value={row.rejection} rising="bad" />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </div>
          )}

          {promises.weighed && (
            <Alert variant="muted">
              <Info />
              <AlertTitle>Metade já pesa na reeleição</AlertTitle>
              <AlertDescription>
                Desde que as chapas fecharam, os grupos votam com metade deste efeito. O balanço do fim do mandato fecha
                a outra metade.
              </AlertDescription>
            </Alert>
          )}
        </div>
      </CardContent>
      <BalanceDialog open={balanceOpen} onOpenChange={setBalanceOpen} />
    </Card>
  );
}
