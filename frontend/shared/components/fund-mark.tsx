import { playerInitials } from "@/shared/lib/player-initials";
import { cn } from "@/shared/lib/utils";

type FundMarkProps = {
  name: string;
  /** `inverse`: sigla na cor da conta sobre fundo claro, para a faixa da cor da conta. */
  tone?: "solid" | "inverse";
  /** A cor da conta: a da gestora ou a do governo (Fundo Soberano) */
  palette?: "fund" | "government";
  size?: "default" | "md" | "lg";
  className?: string;
};

const MARK_COLORS = {
  fund: { solid: "bg-fund text-fund-foreground", inverse: "bg-fund-foreground text-fund" },
  government: {
    solid: "bg-expansion-government text-expansion-government-foreground",
    inverse: "bg-expansion-government-foreground text-expansion-government",
  },
} as const;

/** Selo da gestora: as duas letras do nome sobre a cor da conta. */
export function FundMark({ name, tone = "solid", palette = "fund", size = "default", className }: FundMarkProps) {
  return (
    <span
      aria-hidden
      className={cn(
        "inline-flex shrink-0 items-center justify-center font-bold tracking-tight",
        size === "default" && "size-5 rounded-[5px] text-xs",
        size === "md" && "size-8 rounded-lg text-xs",
        size === "lg" && "size-10 rounded-lg text-base",
        MARK_COLORS[palette][tone],
        className,
      )}
    >
      {playerInitials(name)}
    </span>
  );
}
