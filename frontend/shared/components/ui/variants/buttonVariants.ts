import { cva } from "class-variance-authority";

export const buttonVariants = cva(
  "group/button inline-flex shrink-0 items-center justify-center rounded-lg border border-transparent bg-clip-padding text-sm font-semibold whitespace-nowrap transition-all outline-none select-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 active:not-aria-[haspopup]:translate-y-px disabled:pointer-events-none disabled:opacity-50 aria-invalid:border-destructive aria-invalid:ring-3 aria-invalid:ring-destructive/20 dark:aria-invalid:border-destructive/50 dark:aria-invalid:ring-destructive/40 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary-hover",
        dark: "bg-foreground text-primary-foreground hover:bg-foreground/90",
        // Sobre fundo escuro (barra lateral, hero do fim de partida)
        inverse: "bg-sidebar-accent text-sidebar-accent-foreground hover:bg-sidebar-accent/80",
        outline:
          "border-input bg-card text-foreground hover:bg-subtle aria-expanded:bg-subtle aria-expanded:text-foreground",
        // Gatilho de um painel que fica azul enquanto aberto ("Indicadores" do gráfico)
        "outline-toggle":
          "border-input bg-card text-foreground hover:bg-subtle aria-expanded:border-info-border aria-expanded:bg-info-soft aria-expanded:text-info",
        // Gatilho de um seletor: caixa com borda e o valor escolhido à esquerda
        field:
          "justify-start border-input bg-card px-2.5 font-normal text-foreground hover:bg-subtle aria-expanded:bg-subtle",
        secondary: "bg-secondary text-foreground hover:bg-secondary/80 aria-expanded:bg-secondary",
        ghost: "text-foreground hover:bg-muted aria-expanded:bg-muted",
        destructive:
          "bg-destructive text-destructive-foreground hover:bg-destructive/90 focus-visible:border-destructive/40 focus-visible:ring-destructive/20",
        info: "bg-info-soft text-info hover:bg-info-soft/70 aria-expanded:bg-info-soft",
        success: "bg-success text-success-foreground hover:bg-success/90 focus-visible:ring-success/20",
        warning: "bg-warning text-warning-foreground hover:bg-warning/90 focus-visible:ring-warning/20",
        link: "h-auto px-0 text-primary hover:text-primary-hover",
        "link-destructive": "h-auto px-0 text-destructive hover:text-destructive/80",
        // Ação secundária em texto, ao lado de um título ("Restaurar padrão")
        "link-muted": "h-auto px-0 font-normal text-muted-foreground hover:text-foreground",
      },
      size: {
        default: "h-10 gap-2 px-4",
        xs: "h-6 gap-1 rounded-md px-2 text-xs [&_svg:not([class*='size-'])]:size-3",
        sm: "h-8 gap-1.5 px-3 text-[13px] [&_svg:not([class*='size-'])]:size-3.5",
        lg: "h-11 gap-2 px-5",
        // Altura do conteúdo: botão que carrega mais de uma linha (bloco da corrida na topbar)
        auto: "h-auto gap-3 py-1.5 pr-3 pl-2.5 text-left",
        xl: "h-12 gap-2 px-6 text-base [&_svg:not([class*='size-'])]:size-[18px]",
        icon: "size-10",
        "icon-xs": "size-6 rounded-md [&_svg:not([class*='size-'])]:size-3",
        "icon-sm": "size-8",
        "icon-lg": "size-11",
      },
    },
    compoundVariants: [
      // O link não tem caixa: o espaçamento do tamanho não se aplica
      { variant: ["link", "link-destructive", "link-muted"], className: "px-0" },
    ],
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
);
