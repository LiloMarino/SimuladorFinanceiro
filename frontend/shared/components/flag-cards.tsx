import { Check, Lock } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { FLAGS_PER_PARTY, VALUE_INFO, VOTER_VALUES, lockReason } from "@/shared/lib/party-flags";
import { VALUE_ICONS, tintOf } from "@/shared/lib/value-style";
import { cn } from "@/shared/lib/utils";
import type { VoterValue } from "@/types";

type FlagCardsProps = {
  value: VoterValue[];
  onChange: (value: VoterValue[]) => void;
  /** Linha extra de cada bandeira, como os grupos que ela agrada */
  note?: (flag: VoterValue) => string;
  error?: string | undefined;
};

/** As 6 bandeiras para escolher 3, com a contagem e o bloqueio das que se excluem. */
export function FlagCards({ value, onChange, note, error }: FlagCardsProps) {
  const toggle = (flag: VoterValue) =>
    onChange(value.includes(flag) ? value.filter((item) => item !== flag) : [...value, flag]);
  return (
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
            note={note?.(flag) ?? ""}
            onToggle={() => toggle(flag)}
          />
        ))}
      </div>
      {error && <span className="text-xs text-destructive">{error}</span>}
    </div>
  );
}

type FlagCardProps = {
  flag: VoterValue;
  selected: boolean;
  locked: string | null;
  note: string;
  onToggle: () => void;
};

function FlagCard({ flag, selected, locked, note, onToggle }: FlagCardProps) {
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
        note && <span className="text-[11px] text-muted-foreground">{note}</span>
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
