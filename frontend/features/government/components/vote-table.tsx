import { Bot, Handshake } from "lucide-react";
import { MetricLabel } from "@/shared/components/metric-hint";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { DEFIANCE, FORECAST } from "../lib/government-metrics";
import { causeLabel, rangeLabel, type BlocVote, type Vote } from "../lib/house";
import { OrientationBadge } from "./orientation-badge";
import { PartyMark } from "./party-mark";
import { partyColor } from "@/shared/lib/party-colors";

type VoteTableProps = {
  vote: Vote;
  /** O que a votação decide, na frase da causa: "a medida" */
  subject: string;
  /** A bancada de quem vê, destacada na tabela */
  mineKey?: number | undefined;
};

/** A tabela das bancadas: a orientação e o Sim previsto antes da votação, o resultado depois dela. */
export function VoteTable({ vote, subject, mineKey }: VoteTableProps) {
  const voted = vote.yes !== null;
  const rows = [...vote.blocs].sort((a, b) => b.seats - a.seats || a.key - b.key);

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Bancada</TableHead>
          {voted ? (
            <>
              <TableHead>Orientou</TableHead>
              <TableHead numeric>Sim</TableHead>
              <TableHead numeric>Não</TableHead>
              <TableHead>Contra a orientação</TableHead>
            </>
          ) : (
            <>
              <TableHead>Orientação</TableHead>
              <TableHead>Quem orientou</TableHead>
              <TableHead>
                <MetricLabel metric={DEFIANCE} />
              </TableHead>
              <TableHead numeric>
                <MetricLabel metric={FORECAST} />
              </TableHead>
            </>
          )}
        </TableRow>
      </TableHeader>
      <TableBody>
        {rows.map((bloc) => (
          <TableRow key={bloc.key} variant={bloc.key === mineKey ? "current" : "default"}>
            <TableCell>
              <span className="inline-flex items-center gap-2">
                <PartyMark abbr={bloc.abbr} color={partyColor(bloc)} />
                <span className="font-mono">{bloc.seats}</span>
              </span>
            </TableCell>
            <TableCell>
              <OrientationBadge yes={bloc.orientation} />
            </TableCell>
            {voted ? <VotedCells bloc={bloc} /> : <OpenCells bloc={bloc} subject={subject} />}
          </TableRow>
        ))}
        <TableRow variant="group">
          <TableCell>
            <b>Total</b>
          </TableCell>
          {voted ? (
            <>
              <TableCell />
              <TableCell numeric>
                <b>{vote.yes}</b>
              </TableCell>
              <TableCell numeric>
                <b>{vote.no}</b>
              </TableCell>
              <TableCell>
                <b className="text-warning">{vote.defected}</b>
              </TableCell>
            </>
          ) : (
            <>
              <TableCell />
              <TableCell>
                <span className="text-xs text-muted-foreground">
                  até {vote.blocs.reduce((sum, bloc) => sum + bloc.may_defect, 0)} podem votar contra
                </span>
              </TableCell>
              <TableCell numeric>
                <b className="text-success">{rangeLabel(vote.low, vote.high)}</b>
              </TableCell>
            </>
          )}
        </TableRow>
      </TableBody>
    </Table>
  );
}

function OpenCells({ bloc, subject }: { bloc: BlocVote; subject: string }) {
  // Sim previsto da bancada: do pior caso (todos que podem desobedecer votam contra) ao melhor
  const low = bloc.orientation ? bloc.seats - bloc.may_defect : 0;
  const high = bloc.orientation ? bloc.seats : bloc.may_defect;
  const why = causeLabel(bloc, subject);
  return (
    <>
      <TableCell>
        <span className="inline-flex items-center gap-1.5 text-[13px]">
          {bloc.by_deal ? (
            <>
              <Handshake className="size-3.5 text-primary" />
              Acordo com o governo
            </>
          ) : bloc.guided ? (
            "O líder"
          ) : (
            <>
              <Bot className="size-3.5 text-muted-foreground" />
              {bloc.key < 0 ? "Computador, pelos valores dele" : "Orientação padrão"}
            </>
          )}
        </span>
      </TableCell>
      <TableCell className="whitespace-normal">
        <b className="font-mono">{bloc.may_defect === 0 ? "0" : `até ${bloc.may_defect}`}</b>
        {why && <div className="max-w-60 text-xs text-muted-foreground">{why}</div>}
      </TableCell>
      <TableCell numeric>
        <b>{rangeLabel(low, high)}</b>
      </TableCell>
    </>
  );
}

function VotedCells({ bloc }: { bloc: BlocVote }) {
  return (
    <>
      <TableCell numeric>{bloc.yes}</TableCell>
      <TableCell numeric>{bloc.no}</TableCell>
      <TableCell>
        {bloc.defected ? (
          <b className="text-warning">{`${bloc.defected} votaram ${bloc.orientation ? "Não" : "Sim"}`}</b>
        ) : (
          <span className="text-faint-foreground">—</span>
        )}
      </TableCell>
    </>
  );
}
