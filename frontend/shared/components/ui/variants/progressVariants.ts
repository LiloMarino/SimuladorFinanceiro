import { cva } from "class-variance-authority";

export const progressTrackVariants = cva("relative flex w-full items-center rounded-full", {
  variants: {
    variant: {
      default: "overflow-x-hidden",
      // Trilha com marcadores: eles ficam sobre a trilha e saem dela, então nada é cortado
      markers: "overflow-visible",
    },
    size: {
      default: "h-1",
      sm: "h-1.5",
      md: "h-2",
      lg: "h-3",
    },
    tone: {
      default: "bg-muted",
      // Sobre fundo escuro (hero da corrida, barra lateral)
      inverse: "bg-sidebar-accent",
    },
  },
  defaultVariants: { variant: "default", size: "default", tone: "default" },
});

export const progressIndicatorVariants = cva("h-full rounded-full transition-all", {
  variants: {
    tone: {
      default: "bg-primary",
      inverse: "bg-sidebar-primary",
      // Progresso de quem vê a tela, claro para os marcadores aparecerem sobre ele
      soft: "bg-info-border",
      // Conquistas: o dourado do selo desbloqueado
      gold: "bg-toast-warning",
      // Faixas de uma régua: boa, de atenção e crítica
      success: "bg-success",
      warning: "bg-warning",
      destructive: "bg-destructive",
    },
  },
  defaultVariants: { tone: "default" },
});
