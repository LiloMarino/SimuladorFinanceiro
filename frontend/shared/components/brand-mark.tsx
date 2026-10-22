import { cva, type VariantProps } from "class-variance-authority";

const brandMarkVariants = cva("shrink-0", {
  variants: {
    size: {
      sm: "size-8",
      md: "size-10",
      lg: "size-12",
    },
  },
  defaultVariants: {
    size: "md",
  },
});

/** A rosca de três fatias: a marca do FinSim (mesma geometria de public/logo.svg). */
export function BrandMark({ size }: VariantProps<typeof brandMarkVariants>) {
  return (
    <svg
      className={brandMarkVariants({ size })}
      viewBox="0 0 32 32"
      fill="none"
      strokeWidth={7}
      aria-hidden="true"
    >
      <g transform="rotate(-90 16 16)">
        <circle cx="16" cy="16" r="11" stroke="var(--color-primary)" strokeDasharray="32 37.115" />
        <circle cx="16" cy="16" r="11" stroke="var(--color-chart-2)" strokeDasharray="17 52.115" strokeDashoffset="-35" />
        <circle cx="16" cy="16" r="11" stroke="var(--color-chart-3)" strokeDasharray="11.1 58.015" strokeDashoffset="-55" />
      </g>
    </svg>
  );
}
