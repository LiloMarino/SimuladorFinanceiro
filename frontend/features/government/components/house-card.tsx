import { Info } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent } from "@/shared/components/ui/card";
import { MetricLabel } from "@/shared/components/metric-hint";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { displayDayMonth } from "@/shared/lib/utils/display";
import { DEFECTION_RATE, WITH_GOVERNMENT } from "../lib/government-metrics";
import { blocColor, bySeats, partySeats, seatChange, shareOfVotes, type House } from "../lib/house";
import { Hemicycle } from "./hemicycle";
import { PartyMark } from "./party-mark";

type HouseCardProps = { house: House };

/** O plenário: o hemiciclo por partido e a tabela das bancadas, com o histórico de votos de cada uma. */
export function HouseCard({ house }: HouseCardProps) {
  const blocs = bySeats(house.blocs);
  const computerOnly = house.elected === null;

  return (
    <Card>
      <CardContent>
        <div className="grid min-w-0 content-start gap-3.5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h2 className="text-[15px] font-semibold">Congresso · {house.seats} cadeiras</h2>
            <Badge variant="secondary">
              {house.majority} votos aprovam uma medida · {house.impeachment_votes} derrubam o presidente
            </Badge>
          </div>

          {computerOnly && (
            <Alert variant="info">
              <Info />
              <AlertTitle>A casa ainda é do computador</AlertTitle>
              <AlertDescription>
                Até a primeira eleição, as {house.seats} cadeiras ficam com os três partidos do computador, divididas
                pelo eleitorado de partida.
              </AlertDescription>
            </Alert>
          )}

          <div className="grid gap-5 lg:grid-cols-[420px_minmax(0,1fr)]">
            <div className="grid content-start justify-items-center gap-2.5">
              <Hemicycle
                seats={partySeats(house.blocs)}
                marks={[
                  { at: house.majority, label: `${house.majority}` },
                  { at: house.impeachment_votes, label: `${house.impeachment_votes}` },
                ]}
                label={`Hemiciclo da casa: ${blocs.map((bloc) => `${bloc.abbr} ${bloc.seats}`).join(", ")}`}
              />
              <div className="flex flex-wrap justify-center gap-x-3.5 gap-y-1.5 text-xs text-muted-foreground">
                {blocs.map((bloc) => (
                  <span key={bloc.key} className="inline-flex items-center gap-1.5">
                    <i className="inline-block size-2.5 rounded-full" style={{ backgroundColor: blocColor(bloc) }} />
                    {bloc.abbr} {bloc.seats}
                  </span>
                ))}
              </div>
              {house.elected && (
                <span className="text-xs text-muted-foreground">
                  Eleita em {displayDayMonth(house.elected)}
                  {house.takes_office ? ` · posse em ${displayDayMonth(house.takes_office)}` : ""}
                </span>
              )}
            </div>

            <div className="min-w-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Bancada</TableHead>
                    <TableHead numeric>Cadeiras</TableHead>
                    <TableHead numeric>Mudança</TableHead>
                    <TableHead>
                      <MetricLabel metric={WITH_GOVERNMENT} />
                    </TableHead>
                    <TableHead>
                      <MetricLabel metric={DEFECTION_RATE} />
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {blocs.map((bloc) => (
                    <TableRow key={bloc.key} variant={bloc.is_mine ? "current" : "default"}>
                      <TableCell>
                        <span className="flex min-w-0 items-center gap-2">
                          <PartyMark abbr={bloc.abbr} color={blocColor(bloc)} />
                          <span className="truncate text-[13px]" title={bloc.name}>
                            {bloc.is_computer ? "computador" : bloc.name}
                          </span>
                          {bloc.governing && (
                            <Badge variant="info" size="sm">
                              governo
                            </Badge>
                          )}
                        </span>
                      </TableCell>
                      <TableCell numeric>
                        <b>{bloc.seats}</b>
                      </TableCell>
                      <TableCell numeric>
                        <ChangeCell bloc={bloc} />
                      </TableCell>
                      <TableCell>
                        <span className="text-[13px]">{shareOfVotes(bloc.yes_share, bloc.votes_cast)}</span>
                      </TableCell>
                      <TableCell>
                        <span className="text-[13px]">{shareOfVotes(bloc.defection_share, bloc.votes_cast)}</span>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {house.below.length > 0 && (
                <p className="mt-2.5 rounded-lg bg-subtle px-2.5 py-2 text-xs leading-normal text-muted-foreground">
                  {house.below.join(", ")} ficou abaixo da barreira de {Math.round(Number(house.barrier) * 100)}% e não
                  elegeu deputados.
                </p>
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function ChangeCell({ bloc }: { bloc: House["blocs"][number] }) {
  const change = seatChange(bloc);
  if (change === null) return <span className="text-faint-foreground">—</span>;
  if (change === "0") return <span className="text-faint-foreground">=</span>;
  return <span className={change.startsWith("+") ? "text-success" : "text-destructive"}>{change}</span>;
}
