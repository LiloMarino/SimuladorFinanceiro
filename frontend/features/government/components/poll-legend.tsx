import type { ElectionParty } from "@/types";
import { partyFill } from "../lib/voters";

/** A legenda das barras da pesquisa: um quadrado na cor de cada partido e o dos indecisos. */
export function PollLegend({ parties }: { parties: ElectionParty[] }) {
  return (
    <div className="flex flex-wrap gap-3.5 text-xs text-muted-foreground">
      {parties.map((party) => (
        <span key={party.id} className="inline-flex items-center gap-1.5">
          <span className="size-2.5 rounded-xs" style={{ backgroundColor: partyFill(party) }} />
          {party.abbr}
          {party.candidate && ` · ${party.candidate.name}`}
        </span>
      ))}
      <span className="inline-flex items-center gap-1.5">
        <span className="size-2.5 rounded-xs bg-faint-foreground/40" />
        Indecisos
      </span>
    </div>
  );
}
