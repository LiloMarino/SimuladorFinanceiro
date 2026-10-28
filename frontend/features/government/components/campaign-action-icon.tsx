import { Megaphone, PartyPopper, Swords, Tv, type LucideIcon } from "lucide-react";
import { cn } from "@/shared/lib/utils";
import type { CampaignActionKind } from "@/types";

const ACTION_ICONS: Record<CampaignActionKind, LucideIcon> = {
  TV: Tv,
  EVENT: PartyPopper,
  RALLY: Megaphone,
  ATTACK: Swords,
};

/** O ícone da ação de campanha, num quadrado neutro. */
export function ActionIcon({ kind, className }: { kind: CampaignActionKind; className?: string }) {
  const Icon = ACTION_ICONS[kind];
  return (
    <span
      aria-hidden
      className={cn("inline-flex size-8 shrink-0 items-center justify-center rounded-lg bg-muted", className)}
    >
      <Icon className="size-4" />
    </span>
  );
}
