import { ChartNoAxesColumnIncreasing } from "lucide-react";
import { cva, type VariantProps } from "class-variance-authority";

const brandMarkVariants = cva("flex shrink-0 items-center justify-center bg-primary text-primary-foreground", {
  variants: {
    size: {
      sm: "size-8 rounded-lg [&_svg]:size-[18px]",
      md: "size-10 rounded-[10px] [&_svg]:size-[22px]",
      lg: "size-12 rounded-xl [&_svg]:size-[26px]",
    },
  },
  defaultVariants: {
    size: "md",
  },
});

/** O quadrado azul com as barras: a marca do FinSim. */
export function BrandMark({ size }: VariantProps<typeof brandMarkVariants>) {
  return (
    <span className={brandMarkVariants({ size })} aria-hidden="true">
      <ChartNoAxesColumnIncreasing strokeWidth={2.4} />
    </span>
  );
}
