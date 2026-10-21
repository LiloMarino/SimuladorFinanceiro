import { cva } from "class-variance-authority";

export const badgeVariants = cva(
  "group/badge inline-flex w-fit shrink-0 items-center justify-center gap-1.5 overflow-hidden rounded-full border border-transparent px-2 text-xs font-medium whitespace-nowrap transition-all focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 [&>svg]:pointer-events-none [&>svg]:size-3!",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground",
        secondary: "bg-muted text-secondary-foreground",
        success: "bg-success-soft text-success",
        warning: "bg-warning-soft text-warning",
        destructive: "bg-destructive-soft text-destructive",
        info: "bg-info-soft text-info",
        outline: "border-input bg-card text-foreground",
        // Selo de equipe: a cor vem da variável --team, definida por quem renderiza
        // Selo de equipe sobre fundo escuro: cor cheia e texto branco
        "team-solid": "rounded-md bg-(--team) font-semibold text-white [&>svg]:fill-white [&>svg]:stroke-white",
        team: "rounded-md border-[color-mix(in_srgb,var(--team)_25%,transparent)] bg-[color-mix(in_srgb,var(--team)_8%,transparent)] font-semibold text-foreground [&>svg]:fill-(--team) [&>svg]:stroke-(--team)",
      },
      size: {
        default: "h-6",
        sm: "h-5 px-1.5",
      },
      // Valores e códigos: fonte mono com algarismos alinhados
      numeric: {
        true: "font-mono font-semibold tabular-nums",
        false: "",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
      numeric: false,
    },
  },
);
