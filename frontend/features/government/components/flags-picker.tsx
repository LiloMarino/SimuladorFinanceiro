import { MetricHint } from "@/shared/components/metric-hint";
import { FlagCards } from "@/shared/components/flag-cards";
import { cn } from "@/shared/lib/utils";
import type { ElectionPanel, VoterValue } from "@/types";
import { AFFINITY } from "../lib/election-metrics";
import { VOTER_VALUES } from "@/shared/lib/party-flags";
import { GROUP_INFO, foundingAffinity, groupList, pleasedBy, signedPoints } from "../lib/voters";
import { ProfileRadar } from "./profile-radar";

type FlagsPickerProps = {
  panel: Pick<ElectionPanel, "groups" | "affinity_base" | "radar_neutral" | "radar_flag">;
  value: VoterValue[];
  onChange: (value: VoterValue[]) => void;
  /** Cor do partido no perfil de prévia */
  color: string;
  error?: string | undefined;
};

/** As 6 bandeiras para escolher 3, com o perfil de partida e a afinidade inicial de cada grupo ao lado. */
export function FlagsPicker({ panel, value, onChange, color, error }: FlagsPickerProps) {
  const groups = panel.groups;
  const affinityBase = Number(panel.affinity_base);
  const radar = Object.fromEntries(
    VOTER_VALUES.map((flag) => [flag, Number(value.includes(flag) ? panel.radar_flag : panel.radar_neutral)]),
  ) as Record<VoterValue, number>;

  return (
    <div className="grid gap-5 md:grid-cols-[minmax(0,1fr)_290px]">
      {/* Bandeiras */}
      <FlagCards
        value={value}
        onChange={onChange}
        note={(flag) => {
          const pleased = groupList(pleasedBy(groups, flag));
          return pleased && `Agrada mais: ${pleased}`;
        }}
        error={error}
      />

      {/* Como o eleitorado recebe */}
      <div className="grid content-start gap-3 rounded-lg bg-subtle p-3.5">
        <span className="text-xs font-medium tracking-wide text-muted-foreground uppercase">
          Como o eleitorado recebe
        </span>
        <div className="flex justify-center">
          <ProfileRadar
            width={236}
            height={176}
            label="Perfil de partida do partido"
            series={[{ key: "profile", scores: radar, color }]}
          />
        </div>
        <span className="inline-flex items-center gap-1 text-sm font-medium">
          Afinidade inicial em cada grupo
          <MetricHint metric={AFFINITY} />
        </span>
        <div className="grid gap-1.5">
          {groups.map((group) => (
            <AffinityRow
              key={group.group}
              label={GROUP_INFO[group.group].label}
              change={foundingAffinity(group, value, affinityBase) - affinityBase}
            />
          ))}
        </div>
        <span className="text-xs text-muted-foreground">
          A afinidade é o ponto de partida do apoio: todo partido parte de {affinityBase} em cada grupo, e cada bandeira
          soma o quanto o grupo quer aquele valor. A campanha soma apoio por cima.
        </span>
      </div>
    </div>
  );
}

/** A afinidade do grupo contra a base: verde para a direita quando soma, vermelho para a esquerda quando tira. */
function AffinityRow({ label, change }: { label: string; change: number }) {
  const width = Math.min(Math.abs(change), 50);
  return (
    <div className="grid grid-cols-[1fr_84px_34px] items-center gap-2 text-xs">
      <span className="truncate">{label}</span>
      <span className="relative h-2 rounded-xs bg-muted">
        <span
          className={cn(
            "absolute inset-y-0 rounded-xs",
            change >= 0 ? "left-1/2 bg-success" : "right-1/2 bg-destructive",
          )}
          style={{ width: `${width}%` }}
        />
        <span className="absolute -inset-y-0.5 left-1/2 border-l border-faint-foreground" />
      </span>
      <span
        className={cn(
          "text-right font-mono font-semibold",
          change > 0 ? "text-success" : change < 0 ? "text-destructive" : "text-muted-foreground",
        )}
      >
        {signedPoints(change)}
      </span>
    </div>
  );
}
