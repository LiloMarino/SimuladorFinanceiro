import { cva, type VariantProps } from "class-variance-authority";
import { ChartNoAxesColumnIncreasing } from "lucide-react";

const brandMarkVariants = cva("shrink-0", {
  variants: {
    variant: {
      logo: "",
      square: "flex items-center justify-center bg-primary text-primary-foreground",
    },
    size: {
      sm: "size-8",
      md: "size-10",
      lg: "size-12",
    },
  },
  compoundVariants: [
    { variant: "square", size: "sm", className: "rounded-lg [&_svg]:size-[18px]" },
    { variant: "square", size: "md", className: "rounded-[10px] [&_svg]:size-[22px]" },
    { variant: "square", size: "lg", className: "rounded-xl [&_svg]:size-[26px]" },
  ],
  defaultVariants: {
    variant: "logo",
    size: "md",
  },
});

/**
 * A marca do FinSim. `logo` é a rosca de três fatias (mesma geometria de public/logo.svg);
 * `square` é o quadrado azul com as barras crescentes.
 */
export function BrandMark({ variant, size }: VariantProps<typeof brandMarkVariants>) {
  if (variant === "square") {
    return (
      <span className={brandMarkVariants({ variant, size })} aria-hidden="true">
        <ChartNoAxesColumnIncreasing strokeWidth={2.4} />
      </span>
    );
  }

  return (
    <svg
      className={brandMarkVariants({ variant, size })}
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
