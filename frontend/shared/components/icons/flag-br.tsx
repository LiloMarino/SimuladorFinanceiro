import { forwardRef } from "react";
import type { LucideProps } from "lucide-react";

/** A bandeira do Brasil nas cores do tema; entra onde se espera um `LucideIcon`. */
export const FlagBr = forwardRef<SVGSVGElement, LucideProps>(function FlagBr(
  { size = 24, nonScalingStroke: _nonScalingStroke, ...props },
  ref,
) {
  const width = Number(size);
  return (
    <svg
      ref={ref}
      xmlns="http://www.w3.org/2000/svg"
      width={width}
      height={(width * 2) / 3}
      viewBox="0 0 24 16"
      fill="none"
      aria-hidden="true"
      {...props}
    >
      <rect width="24" height="16" rx="2" className="fill-chart-8" />
      <path d="M12 2.2 21.2 8 12 13.8 2.8 8Z" className="fill-chart-3" />
      <circle cx="12" cy="8" r="3.4" className="fill-chart-1" />
    </svg>
  );
});
