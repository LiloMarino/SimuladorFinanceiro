import { ExpansionEmblem } from "@/shared/components/expansion-emblem";
import { MetricHint } from "@/shared/components/metric-hint";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent } from "@/shared/components/ui/card";
import { useElection } from "@/shared/hooks/queries/useElection";
import type { GovernmentPanel } from "@/types";
import { useToday } from "../hooks/useToday";
import { countdownLabel } from "../lib/election";
import { monthYear } from "../lib/government";
import { PROMISE_VS_DONE } from "../lib/government-metrics";
import { PartyMark, PersonMark } from "./party-mark";
import { PromiseRuler } from "./promise-ruler";

const NUMBER = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 1 });

type GovernmentHeaderProps = { panel: GovernmentPanel };

/** Quem governa, por quanto tempo, e a promessa de campanha contra a média do que o governo aprovou. */
export function GovernmentHeader({ panel }: GovernmentHeaderProps) {
  const { data: election } = useElection();
  const today = useToday(panel);
  const term = panel.term;
  if (!term) return null;

  const party = election?.parties.find((candidate) => candidate.id === term.party_id);
  const president = term.president;
  const mark = panel.approval?.mark;
  const markers = [];
  if (president && term.promise !== null) {
    markers.push({ key: "promise", promise: term.promise, node: <PersonMark person={president} size="sm" /> });
  }
  if (mark) {
    markers.push({
      key: "mark",
      promise: Number(mark),
      node: <span className="block size-2.5 rounded-full border-2 border-card bg-foreground" />,
    });
  }

  return (
    <Card>
      <CardContent>
        <div className="flex flex-wrap items-center gap-4">
          <ExpansionEmblem expansion="government" size="lg" />
          <div className="grid min-w-0 flex-1 gap-1">
            <div className="flex flex-wrap items-center gap-2.5">
              <b className="text-xl">{president ? `Governo ${president.name}` : "Governo neutro do computador"}</b>
              {president && <Badge variant="info">{term.consecutive}º mandato</Badge>}
              {party && <PartyMark abbr={party.abbr} color={party.color} />}
              {term.vice && (
                <Badge variant="secondary">
                  <PersonMark person={term.vice} />
                  vice: {term.vice.name}
                </Badge>
              )}
              {term.succession && <Badge variant="warning">Assumiu por impeachment</Badge>}
            </div>
            <span className="text-[13px] text-muted-foreground">
              {monthYear(term.start)}
              {panel.term_end && ` a ${monthYear(panel.term_end)}`} · próxima eleição em{" "}
              {monthYear(panel.next_election)}, faltam {countdownLabel(today, panel.next_election)} · SELIC com o Banco
              Central
            </span>
          </div>
          {president && term.promise !== null && (
            <div className="grid w-75 gap-1">
              <span className="flex items-center gap-1 text-[11px] font-semibold tracking-[.06em] text-faint-foreground uppercase">
                Promessa × feito
                <MetricHint metric={PROMISE_VS_DONE} />
              </span>
              <PromiseRuler markers={markers} showEnds />
              <span className="text-[11px] text-muted-foreground">
                Avatar: prometido, {term.promise}
                {mark
                  ? ` · ponto preto: a média das aprovadas, ${NUMBER.format(Number(mark))}`
                  : " · nenhuma medida aprovada ainda"}
              </span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
