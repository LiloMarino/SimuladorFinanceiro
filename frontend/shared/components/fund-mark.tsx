import { playerInitials } from "@/shared/lib/player-initials";
import { cn } from "@/shared/lib/utils";

type FundMarkProps = {
  name: string;
  /** `inverse`: sigla verde sobre fundo claro, para a faixa da cor da gestora. */
  tone?: "solid" | "inverse";
  className?: string;
};

/** Selo da gestora: as duas letras do nome sobre a cor da conta. */
export function FundMark({ name, tone = "solid", className }: FundMarkProps) {
  return (
    <span
      aria-hidden
      className={cn(
        "inline-flex size-5 shrink-0 items-center justify-center rounded-[5px] text-xs font-bold tracking-tight",
        tone === "solid" ? "bg-fund text-fund-foreground" : "bg-fund-foreground text-fund",
        className,
      )}
    >
      {playerInitials(name)}
    </span>
  );
}
