import type { ReactNode } from "react";
import { PROMISE_ENDS, rulerPosition } from "../lib/election";

type RulerMarker = {
  key: string | number;
  promise: number;
  node: ReactNode;
};

type PromiseRulerProps = {
  markers: RulerMarker[];
  /** Mostra "Impostos baixos" e "Gasto alto" nas pontas */
  showEnds?: boolean;
};

/** A régua da promessa: do imposto baixo ao gasto alto, com cada marcador na faixa do seu partido. */
export function PromiseRuler({ markers, showEnds = false }: PromiseRulerProps) {
  return (
    <div className="w-full">
      <div className="relative h-6">
        <span className="absolute inset-x-0 top-1/2 h-1.5 -translate-y-1/2 rounded-full bg-linear-to-r from-info-soft via-muted to-warning-soft" />
        {markers.map((marker) => (
          <span
            key={marker.key}
            className="absolute top-1/2 -translate-x-1/2 -translate-y-1/2"
            style={{ left: `${rulerPosition(marker.promise)}%` }}
          >
            {marker.node}
          </span>
        ))}
      </div>
      {showEnds && (
        <div className="mt-1 flex justify-between text-[11px] text-muted-foreground">
          <span>{PROMISE_ENDS.low}</span>
          <span>{PROMISE_ENDS.high}</span>
        </div>
      )}
    </div>
  );
}
