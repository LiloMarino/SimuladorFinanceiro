import { playerInitials } from "@/shared/lib/player-initials";
import { cn } from "@/shared/lib/utils";

type FundMarkProps = {
  name: string;
  /** `inverse`: sigla verde sobre fundo claro, para a faixa da cor da gestora. */
  tone?: "solid" | "inverse";
  size?: "default" | "lg";
  className?: string;
};

/** Selo da gestora: as duas letras do nome sobre a cor da conta. */
export function FundMark({ name, tone = "solid", size = "default", className }: FundMarkProps) {
  return (
    <span
      aria-hidden
      className={cn(
        "inline-flex shrink-0 items-center justify-center font-bold tracking-tight",
        size === "default" ? "size-5 rounded-[5px] text-xs" : "size-10 rounded-lg text-base",
        tone === "solid" ? "bg-fund text-fund-foreground" : "bg-fund-foreground text-fund",
        className,
      )}
    >
      {playerInitials(name)}
    </span>
  );
}
