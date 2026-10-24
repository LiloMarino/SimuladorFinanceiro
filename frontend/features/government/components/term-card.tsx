import { Card, CardContent } from "@/shared/components/ui/card";
import { displayShortDate } from "@/shared/lib/utils/display";
import type { ElectionPanel, ElectionParty } from "@/types";
import { PartyMark, PersonMark } from "./party-mark";

type TermCardProps = { panel: ElectionPanel };

/** O governo em vigor, ou o eleito que toma posse na data marcada. */
export function TermCard({ panel }: TermCardProps) {
  const term = panel.pending_term ?? panel.term;
  if (!term) return null;
  const pending = panel.pending_term !== null;
  const party: ElectionParty | undefined = panel.parties.find((candidate) => candidate.id === term.party_id);

  return (
    <Card>
      <CardContent>
        <div className="grid gap-3">
          <div className="flex items-center justify-between gap-3">
            <h2 className="text-[15px] font-semibold">{pending ? "Eleito, aguardando a posse" : "Governo em vigor"}</h2>
            {party && <PartyMark abbr={party.abbr} color={party.color} />}
          </div>
          {term.president && (
            <div className="flex items-center gap-2.5">
              <PersonMark person={term.president} size="default" />
              <span className="grid gap-px text-[13px]">
                <b className="font-medium">{term.president.name}</b>
                <span className="text-xs text-muted-foreground">
                  Presidente{term.vice ? ` · vice ${term.vice.name}` : " · sem vice"}
                </span>
              </span>
            </div>
          )}
          <span className="text-xs text-muted-foreground">
            {pending
              ? `Toma posse em ${displayShortDate(term.start)}; o mandato dura 4 anos.`
              : `Desde ${displayShortDate(term.start)}${term.consecutive > 1 ? ` · ${term.consecutive}º mandato seguido, sem nova reeleição` : ""}.`}
          </span>
        </div>
      </CardContent>
    </Card>
  );
}
