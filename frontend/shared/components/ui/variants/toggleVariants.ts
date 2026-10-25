import { cva } from "class-variance-authority";

export const toggleVariants = cva(
  "group/toggle inline-flex items-center justify-center gap-1 rounded-lg text-sm font-medium whitespace-nowrap transition-all outline-none hover:bg-muted hover:text-foreground focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 disabled:pointer-events-none disabled:opacity-50 aria-invalid:border-destructive aria-invalid:ring-destructive/20 aria-pressed:bg-muted data-[state=on]:bg-muted dark:aria-invalid:ring-destructive/40 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4",
  {
    variants: {
      variant: {
        default: "bg-transparent",
        outline: "border border-input bg-transparent hover:bg-muted",
        segmented:
          "rounded-md px-3 text-[13px] text-secondary-foreground hover:bg-transparent hover:text-foreground aria-pressed:bg-card aria-pressed:text-foreground aria-pressed:shadow-xs",
        // Troca de modo da página (manual | automático): itens altos, em destaque
        mode: "rounded-[9px] text-[15px] font-semibold text-muted-foreground hover:bg-transparent hover:text-foreground aria-pressed:bg-card aria-pressed:text-foreground aria-pressed:shadow-sm",
      },
      // Cor do item: lado de compra (success), de venda (destructive), de resgate (dark) ou de futuro (future)
      tone: {
        neutral: "",
        success:
          "aria-pressed:bg-success aria-pressed:text-success-foreground aria-pressed:hover:text-success-foreground",
        destructive:
          "aria-pressed:bg-destructive aria-pressed:text-destructive-foreground aria-pressed:hover:text-destructive-foreground",
        dark: "aria-pressed:bg-foreground aria-pressed:text-primary-foreground aria-pressed:hover:text-primary-foreground",
        // Atalho que olha para a frente, no futuro gerado
        future: "text-future-foreground hover:text-future-foreground aria-pressed:text-future-foreground",
      },
      size: {
        // Alternador de modo no rótulo de um campo
        xs: "h-6 min-w-6 px-2.5 text-xs",
        default: "h-8 min-w-8 px-2.5 has-data-[icon=inline-end]:pr-2 has-data-[icon=inline-start]:pl-2",
        sm: "h-7 min-w-7 rounded-[min(var(--radius-md),12px)] px-2.5 text-[0.8rem] has-data-[icon=inline-end]:pr-1.5 has-data-[icon=inline-start]:pl-1.5 [&_svg:not([class*='size-'])]:size-3.5",
        lg: "h-9 min-w-9 px-2.5 has-data-[icon=inline-end]:pr-2 has-data-[icon=inline-start]:pl-2",
        // Grupo segmentado de 40 px de altura total, com os 3 px de trilho de cada lado
        // Item do seletor de modo: 44 px, com o ícone ao lado do rótulo
        mode: "h-11 min-w-8 gap-2 px-[18px] [&_svg:not([class*='size-'])]:size-[18px]",
        field: "h-8.5 min-w-8 px-2.5 has-data-[icon=inline-end]:pr-2 has-data-[icon=inline-start]:pl-2",
      },
    },
    defaultVariants: {
      variant: "default",
      tone: "neutral",
      size: "default",
    },
  },
);
