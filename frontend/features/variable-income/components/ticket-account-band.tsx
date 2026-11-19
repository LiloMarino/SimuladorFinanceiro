import { Briefcase, Landmark } from "lucide-react";
import type { AccountTone } from "@/shared/lib/active-account";
import { cn } from "@/shared/lib/utils";

const BAND_COLORS = {
  fund: { colors: "bg-fund-soft text-fund-strong", Icon: Briefcase },
  government: { colors: "bg-expansion-government-soft text-expansion-government-strong", Icon: Landmark },
} as const;

type TicketAccountBandProps = {
  tone: Exclude<AccountTone, "personal">;
  children: string;
};

/** Cabeçalho da boleta de uma conta que opera: ocupa o topo do card, na cor da conta. */
export function TicketAccountBand({ tone, children }: TicketAccountBandProps) {
  const { colors, Icon } = BAND_COLORS[tone];

  return (
    <div className={cn("-mt-(--card-spacing) flex items-center gap-2.5 px-4 py-2.5 text-[13px] font-semibold", colors)}>
      <Icon className="size-4 shrink-0" aria-hidden />
      <span>{children}</span>
    </div>
  );
}
