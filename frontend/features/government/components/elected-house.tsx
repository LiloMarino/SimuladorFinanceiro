import { Info } from "lucide-react";
import { MetricLabel } from "@/shared/components/metric-hint";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Popover, PopoverContent, PopoverTrigger } from "@/shared/components/ui/popover";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { displayShortDate } from "@/shared/lib/utils/display";
import { BARRIER, DHONDT } from "../lib/government-metrics";
import { partySeats, seatChange, type House } from "../lib/house";
import { Hemicycle } from "./hemicycle";
import { PartyMark } from "./party-mark";
import { partyColor } from "@/shared/lib/party-colors";

const decimal = (value: number, digits: number) => value.toFixed(digits).replace(".", ",");

/** A casa eleita no 1º turno: o hemiciclo, os votos de cada partido, as cadeiras e a mudança desde a casa anterior. */
export function ElectedHouse({ house }: { house: House }) {
  const blocs = [...house.blocs].sort((a, b) => Number(b.votes) - Number(a.votes) || a.key - b.key);
  const out = blocs.filter((bloc) => house.below.includes(bloc.abbr));

  return (
    <div className="grid gap-2.5">
      <div className="flex items-center justify-between gap-3">
        <span className="text-sm font-medium">Congresso eleito · {house.seats} cadeiras</span>
        <DhondtHint house={house} />
      </div>
      <div className="grid justify-items-center gap-1.5">
        <Hemicycle
          seats={partySeats(house.blocs)}
          width={300}
          label={`Hemiciclo da casa eleita: ${blocs.map((bloc) => `${bloc.abbr} ${bloc.seats}`).join(", ")}`}
        />
        <span className="text-xs text-muted-foreground">
          A casa nova toma posse com o presidente
          {house.takes_office ? `, em ${displayShortDate(house.takes_office)}` : ""}. O 2º turno decide só a
          presidência: as cadeiras já estão definidas.
        </span>
      </div>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Partido</TableHead>
            <TableHead numeric>Votos</TableHead>
            <TableHead numeric>Cadeiras</TableHead>
            <TableHead numeric>Antes</TableHead>
            <TableHead numeric>Mudança</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {blocs.map((bloc) => {
            const change = seatChange(bloc);
            return (
              <TableRow key={bloc.key} variant={bloc.is_mine ? "current" : "default"}>
                <TableCell>
                  <PartyMark abbr={bloc.abbr} color={partyColor(bloc)} />
                </TableCell>
                <TableCell numeric>{decimal(Number(bloc.votes), 1)}%</TableCell>
                <TableCell numeric>
                  <b>{bloc.seats}</b>
                </TableCell>
                <TableCell numeric>
                  <span className="text-muted-foreground">{bloc.previous_seats ?? "—"}</span>
                </TableCell>
                <TableCell numeric>
                  {change === null || change === "0" ? (
                    <span className="text-faint-foreground">{change === null ? "—" : "="}</span>
                  ) : (
                    <span className={change.startsWith("+") ? "text-success" : "text-destructive"}>{change}</span>
                  )}
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
      {out.length > 0 && (
        <Alert variant="muted">
          <Info />
          <AlertTitle>{out.map((bloc) => bloc.abbr).join(", ")} fica fora da casa</AlertTitle>
          <AlertDescription>
            Teve menos de {Math.round(Number(house.barrier) * 100)}% dos votos válidos: quem não passa da barreira não
            elege ninguém, e as cadeiras dele vão para os outros partidos.
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}

/** "Como os votos viram cadeiras": a barreira, a divisão por 1, 2, 3 e a última cadeira dada. */
function DhondtHint({ house }: { house: House }) {
  const seated = house.blocs.filter((bloc) => bloc.seats > 0);
  return (
    <Popover>
      <PopoverTrigger type="button">
        <span className="inline-flex items-center gap-1 text-xs font-medium text-info">
          {DHONDT.label}
          <Info className="size-3.5" />
        </span>
      </PopoverTrigger>
      <PopoverContent side="top" className="w-96 max-w-[90vw]">
        <div className="grid gap-2.5 text-[13px]">
          <b>{DHONDT.label}</b>
          <ol className="grid list-decimal gap-1.5 pl-4">
            <li>
              <b>
                <MetricLabel metric={BARRIER} />:
              </b>{" "}
              quem tem menos de {Math.round(Number(house.barrier) * 100)}% dos votos válidos não elege ninguém.
            </li>
            <li>Os votos de cada partido são divididos por 1, 2, 3 e assim por diante.</li>
            <li>As {house.seats} maiores divisões, de qualquer partido, levam uma cadeira cada.</li>
          </ol>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Partido</TableHead>
                <TableHead numeric>÷1</TableHead>
                <TableHead numeric>÷2</TableHead>
                <TableHead numeric>última que entra</TableHead>
                <TableHead numeric>cad.</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {seated.map((bloc) => (
                <TableRow key={bloc.key}>
                  <TableCell>{bloc.abbr}</TableCell>
                  <TableCell numeric>{decimal(Number(bloc.votes), 1)}</TableCell>
                  <TableCell numeric>{decimal(Number(bloc.votes) / 2, 1)}</TableCell>
                  <TableCell numeric>
                    ÷{bloc.seats} = {decimal(Number(bloc.votes) / bloc.seats, 3)}
                  </TableCell>
                  <TableCell numeric>
                    <b>{bloc.seats}</b>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          <span className="text-xs text-muted-foreground">
            A última cadeira valeu {decimal(Number(house.last_quotient), 3)} votos por cadeira; a próxima, que ficou de
            fora, valeria {decimal(Number(house.next_quotient), 3)}.
          </span>
        </div>
      </PopoverContent>
    </Popover>
  );
}
