import { baseShare } from "../lib/treasury";

type RateBarProps = { base: string; rate: string };

/** A taxa em barra: o cinza é a parte base e o âmbar que sobra é o prêmio de risco do país. */
export function RateBar({ base, rate }: RateBarProps) {
  return (
    <span aria-hidden className="flex h-1.5 w-40 overflow-hidden rounded-full bg-muted">
      <span className="bg-risk-base" style={{ width: `${baseShare(base, rate)}%` }} />
      <span className="flex-1 bg-risk-premium" />
    </span>
  );
}
