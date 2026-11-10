import type { CSSProperties } from "react";
import { Trophy } from "lucide-react";
import { PartyMark } from "@/shared/components/party-mark";
import { partyColor } from "@/shared/lib/party-colors";
import { displayPoints } from "@/shared/lib/political-capital";
import { cn } from "@/shared/lib/utils";
import type { OverviewReport } from "@/types";
import { PodiumSteps } from "./podium-steps";

/** Pódio de partidos: o degrau é da cor do partido, com a sigla, os pontos de capital político e a distância do líder. */
export function PartyPodium({ report }: { report: OverviewReport }) {
  return (
    <PodiumSteps
      items={report.parties}
      emptyLabel={(position) => `Sem ${position}º partido`}
      columnStyle={(party) => ({ "--party": partyColor(party) }) as CSSProperties}
      stepClassName={(party) => (party ? "bg-(--party)" : "bg-sidebar-accent")}
      renderEntry={(party, first) => (
        <>
          {first && <Trophy className="size-[26px] text-trophy" />}
          <PartyMark abbr={party.abbr} color={party.color} size="lg" />
          <span className="max-w-full truncate text-[13px] font-semibold text-white">{party.name}</span>
          <span className={cn("font-mono text-[13px]", first ? "text-trophy" : "text-sidebar-muted")}>
            {displayPoints(party.capital.total)}
          </span>
          <span className="max-w-full truncate text-xs text-sidebar-muted">
            {party.members.length} {party.members.length === 1 ? "filiado" : "filiados"}
          </span>
          {!first && (
            <span className="text-xs text-sidebar-muted">
              {party.leader_gap === 0 ? "empatado em pontos" : `a ${displayPoints(party.leader_gap)} do líder`}
            </span>
          )}
        </>
      )}
    />
  );
}
