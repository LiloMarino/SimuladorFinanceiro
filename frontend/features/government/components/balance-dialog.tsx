import { RefreshCw, TriangleAlert } from "lucide-react";
import { MetricHint } from "@/shared/components/metric-hint";
import { Alert, AlertAction, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import {
  Dialog,
  DialogBody,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/shared/components/ui/dialog";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { displayShortDate } from "@/shared/lib/utils/display";
import type { PromiseBalance } from "@/types";
import { useBalances } from "../hooks/queries/useBalances";
import { AFFINITY, REJECTION } from "../lib/election-metrics";
import { PROMISE_STATE, stateLabel } from "../lib/promises";
import { GROUP_INFO } from "../lib/voters";
import { PartyMark } from "./party-mark";
import { SignedDecimal } from "./signed-decimal";
import { GroupIcon } from "./value-chip";

type BalanceDialogProps = { open: boolean; onOpenChange: (open: boolean) => void };

/** O balanço das promessas dos governos que acabaram: o estado de cada promessa e, para os filiados, o que ela deixou em cada grupo. */
export function BalanceDialog({ open, onOpenChange }: BalanceDialogProps) {
  const query = useBalances(open);
  const balances = query.data;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-200">
        <DialogHeader variant="divided">
          <DialogTitle>Balanço das promessas</DialogTitle>
          <DialogDescription>
            Vale o que estava em vigor no último dia do mandato. Cumprida soma afinidade e repara a rejeição de quem
            queria a medida; descumprida soma rejeição.
          </DialogDescription>
        </DialogHeader>
        <DialogBody>
          {balances ? (
            balances.length > 0 ? (
              <div className="grid gap-6">
                {balances.map((balance) => (
                  <BalanceView key={`${balance.party_id}|${balance.date}`} balance={balance} />
                ))}
              </div>
            ) : (
              <p className="py-6 text-center text-sm text-muted-foreground">Nenhum governo fechou o balanço ainda.</p>
            )
          ) : query.isError ? (
            <Alert variant="destructive">
              <TriangleAlert />
              <AlertTitle>Não deu para carregar o balanço</AlertTitle>
              <AlertDescription>{query.error.message}</AlertDescription>
              <AlertAction>
                <Button size="sm" variant="outline" onClick={() => void query.refetch()}>
                  <RefreshCw />
                  Tentar de novo
                </Button>
              </AlertAction>
            </Alert>
          ) : (
            <div className="grid gap-3" aria-busy="true" aria-label="Carregando o balanço">
              <Skeleton className="h-10" />
              <Skeleton className="h-40" />
            </div>
          )}
        </DialogBody>
        <DialogFooter variant="divided" className="sm:justify-end">
          <Button onClick={() => onOpenChange(false)}>Fechar</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function BalanceView({ balance }: { balance: PromiseBalance }) {
  const showEffects = balance.totals.length > 0;

  return (
    <section className="grid gap-3">
      <div className="flex flex-wrap items-center gap-2.5">
        <PartyMark abbr={balance.party_abbr} color={balance.party_color} size="md" />
        <b className="text-[15px]">
          Governo do {balance.party_abbr}, de {displayShortDate(balance.term_start)} a {displayShortDate(balance.date)}
        </b>
        {balance.impeached && (
          <Badge variant="destructive" size="sm">
            terminou em impeachment
          </Badge>
        )}
      </div>

      <div className="grid gap-px overflow-hidden rounded-lg border bg-border">
        {balance.items.map((item) => (
          <div
            key={item.promise.title}
            className="flex flex-wrap items-center justify-between gap-2 bg-card px-3.5 py-2.5"
          >
            <b className="text-[13px]" title={item.promise.title}>
              {item.promise.title}
            </b>
            <Badge variant={PROMISE_STATE[item.state].variant} size="sm">
              {stateLabel(item.state, item.done)}
            </Badge>
          </div>
        ))}
      </div>

      {showEffects ? (
        <div className="grid gap-2">
          <div className="flex items-baseline justify-between gap-2">
            <b className="text-sm">O que o mandato deixou em cada grupo</b>
            <Badge variant="secret" size="sm">
              Só o {balance.party_abbr} vê estes números
            </Badge>
          </div>
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
                {balance.totals.map((row) => (
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
          <span className="text-xs leading-normal text-muted-foreground">
            Afinidade é a parte do apoio que não cai com o tempo. Rejeição só cai com reparação: promessa cumprida ao
            grupo, mês de governo aprovado ou evento de campanha.
          </span>
        </div>
      ) : (
        <p className="text-xs text-muted-foreground">
          O estado de cada promessa é público; o que ela deixou em cada grupo, só o {balance.party_abbr} vê.
        </p>
      )}
    </section>
  );
}
