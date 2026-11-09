import { forwardRef } from "react";
import type { LucideProps } from "lucide-react";

/** A bandeira dos Estados Unidos nas cores do tema; entra onde se espera um `LucideIcon`. */
export const FlagUs = forwardRef<SVGSVGElement, LucideProps>(function FlagUs(
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
      <rect width="24" height="16" rx="2" className="fill-white" />
      {/* Listras vermelhas */}
      <path
        d="M0 2a2 2 0 0 1 2-2h20a2 2 0 0 1 2 2v1.3H0Zm0 4h24v1.4H0Zm0 4.1h24v1.4H0ZM0 14.3h24V14a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2Z"
        className="fill-destructive"
      />
      {/* Quadro azul */}
      <path d="M2 0h10v8.6H0V2a2 2 0 0 1 2-2Z" className="fill-info" />
    </svg>
  );
});
