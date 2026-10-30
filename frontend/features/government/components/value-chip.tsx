import { Briefcase, ChartLine, HandHeart, HardHat, Store, Armchair, type LucideIcon } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { cn } from "@/shared/lib/utils";
import type { VoterGroup, VoterValue } from "@/types";
import { VALUE_ICONS, tintOf } from "@/shared/lib/value-style";
import { VALUE_INFO } from "@/shared/lib/party-flags";

const GROUP_ICONS: Record<VoterGroup, LucideIcon> = {
  INVESTORS: ChartLine,
  ENTREPRENEURS: Store,
  FORMAL_WORKERS: HardHat,
  PUBLIC_SERVANTS: Briefcase,
  RETIREES: Armchair,
  WELFARE: HandHeart,
};

/** A bandeira como selo: ícone e nome na cor dela. */
export function ValueChip({ value }: { value: VoterValue }) {
  const Icon = VALUE_ICONS[value];
  return (
    <Badge variant="tint" size="sm" style={tintOf(value)}>
      <Icon />
      {VALUE_INFO[value].label}
    </Badge>
  );
}

/** As bandeiras do partido em fila; sem bandeiras, o aviso de que o perfil está neutro. */
export function ValueChips({ values }: { values: VoterValue[] | null }) {
  if (values === null) {
    return (
      <Badge variant="warning" size="sm">
        Bandeiras por escolher
      </Badge>
    );
  }
  return (
    <span className="flex flex-wrap gap-1">
      {values.map((value) => (
        <ValueChip key={value} value={value} />
      ))}
    </span>
  );
}

/** O ícone do grupo de eleitores, num quadrado neutro. */
export function GroupIcon({ group, className }: { group: VoterGroup; className?: string }) {
  const Icon = GROUP_ICONS[group];
  return (
    <span
      aria-hidden
      className={cn(
        "inline-flex size-8 shrink-0 items-center justify-center rounded-lg bg-muted text-muted-foreground",
        className,
      )}
    >
      <Icon className="size-4" />
    </span>
  );
}
