import { ExpansionEmblem } from "@/shared/components/expansion-emblem";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent } from "@/shared/components/ui/card";
import { useElection } from "@/shared/hooks/queries/useElection";
import type { GovernmentPanel } from "@/types";
import { useToday } from "../hooks/useToday";
import { countdownLabel } from "../lib/election";
import { isComputerGovernment, monthYear } from "../lib/government";
import { PartyMark, PersonMark } from "./party-mark";
import { ValueChips } from "./value-chip";

type GovernmentHeaderProps = { panel: GovernmentPanel };

/** Quem governa, por quanto tempo, e as bandeiras do partido no governo. */
export function GovernmentHeader({ panel }: GovernmentHeaderProps) {
  const { data: election } = useElection();
  const today = useToday(panel);
  const term = panel.term;
  if (!term) return null;

  const party = election?.parties.find((candidate) => candidate.id === term.party_id);
  const president = term.president;

  return (
    <Card>
      <CardContent>
        <div className="flex flex-wrap items-center gap-4">
          <ExpansionEmblem expansion="government" size="lg" />
          <div className="grid min-w-0 flex-1 gap-1">
            <div className="flex flex-wrap items-center gap-2.5">
              <b className="text-xl">{president ? `Governo ${president.name}` : "Governo neutro do computador"}</b>
              {president &&
                (isComputerGovernment(term) ? (
                  <Badge variant="secondary">computador</Badge>
                ) : (
                  <Badge variant="info">{term.consecutive}º mandato</Badge>
                ))}
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
          {party && (
            <div className="grid gap-1">
              <span className="text-[11px] font-semibold tracking-[.06em] text-faint-foreground uppercase">
                Bandeiras do {party.abbr}
              </span>
              <ValueChips values={party.flags} />
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
