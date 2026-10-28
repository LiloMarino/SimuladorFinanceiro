import { Check, Lock } from "lucide-react";
import { MetricHint } from "@/shared/components/metric-hint";
import { Badge } from "@/shared/components/ui/badge";
import { cn } from "@/shared/lib/utils";
import type { ElectionPanel, VoterValue } from "@/types";
import { AFFINITY } from "../lib/election-metrics";
import {
  FLAGS_PER_PARTY,
  GROUP_INFO,
  VALUE_INFO,
  VOTER_VALUES,
  foundingAffinity,
  groupList,
  lockReason,
  pleasedBy,
  signedPoints,
} from "../lib/voters";
import { ProfileRadar } from "./profile-radar";
import { VALUE_ICONS, tintOf } from "../lib/value-style";

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
  const toggle = (flag: VoterValue) =>
    onChange(value.includes(flag) ? value.filter((item) => item !== flag) : [...value, flag]);
  const radar = Object.fromEntries(
    VOTER_VALUES.map((flag) => [flag, Number(value.includes(flag) ? panel.radar_flag : panel.radar_neutral)]),
  ) as Record<VoterValue, number>;

  return (
    <div className="grid gap-5 md:grid-cols-[minmax(0,1fr)_290px]">
      {/* Bandeiras */}
      <div className="grid content-start gap-2.5">
        <div className="flex items-baseline justify-between">
          <span className="text-sm font-medium">Bandeiras · escolha 3</span>
          <span
            className={cn(
              "font-mono text-[13px] font-semibold",
              value.length === FLAGS_PER_PARTY ? "text-success" : "text-muted-foreground",
            )}
          >
            {value.length} de {FLAGS_PER_PARTY}
          </span>
        </div>
        <span className="text-xs text-muted-foreground">
          As bandeiras ficam para sempre. O perfil do partido parte delas e depois se move com o que ele faz no governo.
        </span>
        <div role="group" aria-label="Bandeiras do partido" className="grid grid-cols-2 gap-2.5 sm:grid-cols-3">
          {VOTER_VALUES.map((flag) => (
            <FlagCard
              key={flag}
              flag={flag}
              selected={value.includes(flag)}
              locked={lockReason(flag, value)}
              pleased={groupList(pleasedBy(groups, flag))}
              onToggle={() => toggle(flag)}
            />
          ))}
        </div>
        {error && <span className="text-xs text-destructive">{error}</span>}
      </div>

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

type FlagCardProps = {
  flag: VoterValue;
  selected: boolean;
  locked: string | null;
  pleased: string;
  onToggle: () => void;
};

function FlagCard({ flag, selected, locked, pleased, onToggle }: FlagCardProps) {
  const Icon = VALUE_ICONS[flag];
  const info = VALUE_INFO[flag];
  return (
    <button
      type="button"
      role="checkbox"
      aria-checked={selected}
      disabled={locked !== null}
      onClick={onToggle}
      style={tintOf(flag)}
      className={cn(
        "relative grid content-start gap-1 rounded-lg border bg-card p-3 text-left transition-colors outline-none focus-visible:ring-3 focus-visible:ring-ring/50",
        selected ? "border-primary ring-1 ring-primary" : "hover:border-input",
        locked !== null && "cursor-not-allowed opacity-60",
      )}
    >
      <span className="inline-flex size-7.5 items-center justify-center rounded-md bg-[color-mix(in_srgb,var(--tint)_12%,transparent)] text-(--tint)">
        <Icon className="size-4" />
      </span>
      <b className="mt-0.5 text-sm font-semibold">{info.label}</b>
      <span className="text-xs text-muted-foreground">{info.description}</span>
      {locked !== null ? (
        <Badge variant="secondary" size="sm" className="mt-0.5 h-auto min-h-5 whitespace-normal">
          <Lock />
          {locked}
        </Badge>
      ) : (
        pleased && <span className="text-[11px] text-muted-foreground">Agrada mais: {pleased}</span>
      )}
      <span
        aria-hidden
        className={cn(
          "absolute top-3 right-3 inline-flex size-4.5 items-center justify-center rounded-full",
          selected ? "bg-primary text-primary-foreground" : "border-[1.5px] border-input",
        )}
      >
        {selected && <Check className="size-3" strokeWidth={3} />}
      </span>
    </button>
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
