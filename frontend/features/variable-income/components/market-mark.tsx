import { cva, type VariantProps } from "class-variance-authority";

const marketMarkVariants = cva("flex shrink-0 items-center justify-center rounded-[28%] bg-foreground", {
  variants: {
    size: {
      sm: "size-[22px]",
      md: "size-8",
      lg: "size-12",
      xl: "size-16",
    },
  },
  defaultVariants: {
    size: "md",
  },
});

/**
 * A marca do Mercado: único avatar quadrado do app (jogador é círculo).
 * O navy fica fora da paleta de cores dos jogadores; o nome "Mercado" aparece sempre ao lado.
 */
export function MarketMark({ size }: VariantProps<typeof marketMarkVariants>) {
  return (
    <span className={marketMarkVariants({ size })} aria-hidden="true">
      <svg viewBox="0 0 24 24" fill="none" strokeLinecap="round" className="size-[72%]">
        <path d="M6 4v16M12 3v18M18 6v13" strokeWidth="1.6" className="stroke-toast-info" />
        <rect x="4" y="8" width="4" height="7" rx="1" className="fill-toast-foreground" />
        <rect x="10" y="6" width="4" height="9" rx="1" className="fill-toast-success" />
        <rect x="16" y="10" width="4" height="6" rx="1" className="fill-toast-foreground" />
      </svg>
    </span>
  );
}
