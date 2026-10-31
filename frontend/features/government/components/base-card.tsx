import { useState } from "react";
import { Handshake, Info, TriangleAlert } from "lucide-react";
import { MetricHint, MetricLabel } from "@/shared/components/metric-hint";
import { Kpi } from "@/shared/components/kpi";
import { Alert, AlertAction, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { CardState } from "@/shared/components/card-state";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { displayDayMonth } from "@/shared/lib/utils/display";
import type { BaseDeal, CongressBase } from "@/types";
import { useWithdrawDeal } from "../hooks/mutations/useWithdrawDeal";
import { useBase } from "../hooks/queries/useBase";
import {
  daysLeftLabel,
  dealsInForce,
  dealsPending,
  baseSeats,
  majorityMargin,
  monthlyLabel,
  outsideLabel,
  pendingLabel,
  yearShare,
} from "../lib/base";
import { AMENDMENTS, BASE_DEFECTION, BASE_SEATS } from "../lib/government-metrics";
import { BreakDealDialog } from "./break-deal-dialog";
import { Hemicycle } from "./hemicycle";
import { NegotiateDialog } from "./negotiate-dialog";
import { PartyMark } from "./party-mark";
import { ProposalNotice } from "./proposal-notice";
import { partyColor } from "@/shared/lib/party-colors";

type Breaking = { deal: BaseDeal; side: "government" | "ally" };
type Negotiating = { round: number; key: number | null };

/** A base do governo no Congresso: quem orienta Sim, o que a emenda custa e como negociar ou romper. */
export function BaseCard() {
  const { data: base, error, refetch } = useBase();

  if (!base) {
    return (
      <CardState
        title="Base no Congresso"
        label="Carregando a base do governo"
        error={error}
        onRetry={() => void refetch()}
        errorTitle="Não deu para carregar a base."
        errorDescription="O resto do Governo continua funcionando. Os acordos seguem valendo enquanto isso."
      >
        <div className="flex items-end gap-4">
          <Skeleton className="h-25 w-50" />
          <div className="grid flex-1 gap-2">
            <Skeleton className="h-11.5" />
            <Skeleton className="h-11.5" />
          </div>
        </div>
        <Skeleton className="h-3.5 w-[70%]" />
      </CardState>
    );
  }
  return <BaseContent base={base} />;
}

function BaseContent({ base }: { base: CongressBase }) {
  const [breaking, setBreaking] = useState<Breaking | null>(null);
  const [negotiating, setNegotiating] = useState<Negotiating | null>(null);
  const withdraw = useWithdrawDeal();

  const active = dealsInForce(base);
  const pending = dealsPending(base);
  const governing = base.blocs.find((bloc) => bloc.governing);
  const margin = majorityMargin(base.seats, base.majority);
  const outside = outsideLabel(base.blocs);
  const ownMajority = base.governing_seats >= base.majority;
  const renewing = base.is_president ? active.filter((deal) => deal.renewable) : [];
  const hasDeals = active.length > 0;

  const negotiate = (key: number | null) => setNegotiating({ round: (negotiating?.round ?? 0) + 1, key });

  return (
    <Card>
      <CardContent>
        <div className="grid gap-4">
          {/* Cabeçalho */}
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div className="grid gap-1">
              <h2 className="text-[15px] font-semibold">Base no Congresso</h2>
              <span className="text-[13px] text-muted-foreground">
                Os partidos que orientam Sim em tudo o que o governo propõe: o do presidente e os aliados pagos com
                emenda. A emenda é gasto como outro qualquer.
              </span>
            </div>
            {base.is_president ? (
              <Button size="sm" disabled={base.blocker !== null} onClick={() => negotiate(null)}>
                <Handshake />
                Negociar apoio
              </Button>
            ) : (
              <Badge variant="secondary">a sala vê</Badge>
            )}
          </div>

          {base.is_president && base.blocker && (
            <Alert variant="muted">
              <Info />
              <AlertDescription>{base.blocker}</AlertDescription>
            </Alert>
          )}

          {/* Avisos fixos: a proposta que espera o líder, o acordo do aliado e as renovações */}
          <ProposalNotice base={base} />
          {base.my_deal && base.my_deal.status === "ACTIVE" && base.my_deal.end && (
            <Alert variant="info">
              <Handshake />
              <AlertTitle>
                O {base.my_deal.abbr} está na base do governo até {displayDayMonth(base.my_deal.end)}
              </AlertTitle>
              <AlertDescription>
                Você recebe {monthlyLabel(base.my_deal.monthly)} por mês de emenda e orienta Sim nas medidas do governo.
              </AlertDescription>
              <AlertAction>
                <Button size="xs" variant="outline" onClick={() => setBreaking({ deal: base.my_deal!, side: "ally" })}>
                  Sair da base
                </Button>
              </AlertAction>
            </Alert>
          )}
          {renewing.map((deal) => (
            <Alert key={deal.id} variant="warning">
              <TriangleAlert />
              <AlertTitle>
                O acordo com o {deal.abbr} acaba em {deal.end ? displayDayMonth(deal.end) : "breve"}
              </AlertTitle>
              <AlertDescription>
                Sem proposta nova, ele acaba sem quebra e a base cai para {deal.base_after} cadeiras. Pelo preço de
                hoje: {monthlyLabel(base.blocs.find((bloc) => bloc.key === deal.bloc_key)?.monthly ?? deal.monthly)} por
                mês.
              </AlertDescription>
              <AlertAction>
                <Button size="xs" onClick={() => negotiate(deal.bloc_key)} disabled={base.blocker !== null}>
                  Propor de novo
                </Button>
              </AlertAction>
            </Alert>
          ))}

          {/* Situação da maioria */}
          {base.is_president && !hasDeals && !ownMajority && (
            <Alert variant="info">
              <Info />
              <AlertTitle>
                Só o {base.governing_abbr ?? "governo"} na base: {margin.text}
              </AlertTitle>
              <AlertDescription>
                Sem maioria, cada medida depende de como as outras bancadas orientam. Negocie apoio por emenda.
              </AlertDescription>
            </Alert>
          )}
          {base.is_president && ownMajority && (
            <Alert variant="success">
              <Info />
              <AlertTitle>
                O {base.governing_abbr ?? "governo"} tem maioria sozinho: {base.governing_seats} cadeiras
              </AlertTitle>
              <AlertDescription>
                Nenhum acordo é preciso. Negociar ainda serve para ter folga contra a desobediência ou contra o
                impeachment.
              </AlertDescription>
            </Alert>
          )}

          <div className="grid gap-5 lg:grid-cols-[400px_minmax(0,1fr)]">
            {/* Hemiciclo da base */}
            <div className="grid content-start justify-items-center gap-2.5">
              <Hemicycle
                seats={baseSeats(base.blocs)}
                marks={[
                  { at: base.majority, label: `${base.majority}` },
                  { at: base.impeachment_votes, label: `${base.impeachment_votes}` },
                ]}
                label={`Hemiciclo da base: ${base.blocs.map((bloc) => `${bloc.abbr} ${bloc.seats}`).join(", ")}`}
              />
              <div className="flex flex-wrap justify-center gap-x-3.5 gap-y-1.5 text-xs text-muted-foreground">
                {base.blocs.map((bloc) => (
                  <span key={bloc.key} className="inline-flex items-center gap-1.5">
                    <i className="inline-block size-2.5 rounded-full" style={{ backgroundColor: partyColor(bloc) }} />
                    {bloc.abbr} {bloc.seats}
                  </span>
                ))}
              </div>
            </div>

            <div className="grid min-w-0 content-start gap-3.5">
              {/* Indicadores */}
              <div className="grid gap-2.5 sm:grid-cols-3">
                <Kpi
                  label={
                    <>
                      {BASE_SEATS.label}
                      <MetricHint metric={BASE_SEATS} />
                    </>
                  }
                  value={base.seats}
                  tone={margin.enough ? "success" : "warning"}
                  note={margin.text}
                />
                <Kpi
                  label={
                    <>
                      {AMENDMENTS.label}
                      <MetricHint metric={AMENDMENTS} />
                    </>
                  }
                  value={monthlyLabel(base.amendments.monthly)}
                  note={`por mês · ${yearShare(base.amendments.ratio)} do PIB por ano`}
                />
                <Kpi
                  label={
                    <>
                      {BASE_DEFECTION.label}
                      <MetricHint metric={BASE_DEFECTION} />
                    </>
                  }
                  value={base.last_vote ? base.last_vote.defected : "—"}
                  note={
                    base.last_vote
                      ? `${base.last_vote.defected === 1 ? "deputado da base votou" : "deputados da base votaram"} Não em ${displayDayMonth(base.last_vote.day)}`
                      : "ainda sem votação com a base"
                  }
                />
              </div>

              {/* Tabela da base */}
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Partido</TableHead>
                    <TableHead numeric>Cadeiras</TableHead>
                    <TableHead numeric>
                      <MetricLabel metric={AMENDMENTS} />
                    </TableHead>
                    <TableHead>Prazo</TableHead>
                    <TableHead>Orientou</TableHead>
                    <TableHead />
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {governing && (
                    <TableRow variant="current">
                      <TableCell>
                        <span className="flex items-center gap-2">
                          <PartyMark abbr={governing.abbr} color={partyColor(governing)} />
                          <span className="text-xs text-muted-foreground">· governo</span>
                        </span>
                      </TableCell>
                      <TableCell numeric>
                        <b>{governing.seats}</b>
                      </TableCell>
                      <TableCell numeric>
                        <Dash />
                      </TableCell>
                      <TableCell>
                        <Dash />
                      </TableCell>
                      <TableCell>
                        <Dash />
                      </TableCell>
                      <TableCell />
                    </TableRow>
                  )}
                  {active.map((deal) => (
                    <TableRow key={deal.id}>
                      <TableCell>
                        <span className="flex min-w-0 items-center gap-2">
                          <PartyMark abbr={deal.abbr} color={partyColor(deal)} />
                          {deal.centrao && (
                            <Badge variant="secondary" size="sm">
                              centrão
                            </Badge>
                          )}
                        </span>
                      </TableCell>
                      <TableCell numeric>
                        <b>{deal.seats}</b>
                      </TableCell>
                      <TableCell numeric>{monthlyLabel(deal.monthly)}</TableCell>
                      <TableCell>
                        <span className="grid text-[13px]">
                          {deal.end ? `até ${displayDayMonth(deal.end)}` : "—"}
                          {deal.days_left !== null && (
                            <span className="text-xs text-muted-foreground">{daysLeftLabel(deal.days_left)}</span>
                          )}
                        </span>
                      </TableCell>
                      <TableCell>
                        <span className="text-[13px] text-success">
                          {deal.votes > 0 ? `Sim em ${deal.yes} de ${deal.votes}` : "sem votação"}
                        </span>
                      </TableCell>
                      <TableCell className="text-right">
                        {base.is_president && (
                          <Button
                            size="xs"
                            variant="outline-destructive"
                            onClick={() => setBreaking({ deal, side: "government" })}
                          >
                            Romper
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                  {pending.map((deal) => (
                    <TableRow key={deal.id}>
                      <TableCell>
                        <span className="flex min-w-0 items-center gap-2">
                          <PartyMark abbr={deal.abbr} color={partyColor(deal)} />
                          {deal.centrao && (
                            <Badge variant="secondary" size="sm">
                              centrão
                            </Badge>
                          )}
                        </span>
                      </TableCell>
                      <TableCell numeric>
                        <b>{deal.seats}</b>
                      </TableCell>
                      <TableCell numeric>{monthlyLabel(deal.monthly)}</TableCell>
                      <TableCell colSpan={2}>
                        <span className="text-[13px] text-muted-foreground">{pendingLabel(deal)}</span>
                      </TableCell>
                      <TableCell className="text-right">
                        {base.is_president && (
                          <Button
                            size="xs"
                            variant="outline"
                            disabled={withdraw.isPending}
                            onClick={() => withdraw.mutate(deal.id)}
                          >
                            Cancelar proposta
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                  {hasDeals && (
                    <TableRow variant="group">
                      <TableCell variant="group">Total das emendas</TableCell>
                      <TableCell />
                      <TableCell variant="group" numeric>
                        {monthlyLabel(base.amendments.monthly)}
                      </TableCell>
                      <TableCell variant="note" colSpan={3}>
                        {yearShare(base.amendments.ratio)} do PIB/ano, no gasto
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>

              {outside && (
                <p className="text-xs leading-normal text-muted-foreground">
                  Fora da base: {outside}. Romper antes do prazo faz os grupos do aliado somarem rejeição ao partido do
                  governo.
                </p>
              )}
            </div>
          </div>
        </div>

        {breaking && (
          <BreakDealDialog
            open
            onOpenChange={(open) => !open && setBreaking(null)}
            base={base}
            deal={breaking.deal}
            side={breaking.side}
          />
        )}
        {negotiating && (
          <NegotiateDialog
            key={negotiating.round}
            open
            onOpenChange={(open) => !open && setNegotiating(null)}
            base={base}
            initialKey={negotiating.key}
          />
        )}
      </CardContent>
    </Card>
  );
}

function Dash() {
  return <span className="text-faint-foreground">—</span>;
}
