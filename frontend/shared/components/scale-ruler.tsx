import { displayNumber } from "@/shared/lib/utils/display";

type ScaleRulerProps = {
  /** Valor de hoje; nulo quando o indicador ainda não tem leitura */
  value: number | null;
  /** Abaixo dele a leitura é de compra; acima de `high`, de venda */
  low: number;
  high: number;
};

/** Régua de 0 a 100 com as faixas de leitura e a marca de onde o valor de hoje está. */
export function ScaleRuler({ value, low, high }: ScaleRulerProps) {
  const position = value === null ? null : Math.min(Math.max(value, 0), 100);

  return (
    <div className="grid gap-1 pt-1">
      <div className="relative h-2 rounded-full bg-current/15">
        <span className="absolute inset-y-0 left-0 rounded-l-full bg-current/30" style={{ width: `${low}%` }} />
        <span className="absolute inset-y-0 right-0 rounded-r-full bg-current/30" style={{ width: `${100 - high}%` }} />
        {position !== null && (
          <span
            className="absolute top-1/2 size-3 -translate-x-1/2 -translate-y-1/2 rounded-full bg-current ring-2 ring-popover"
            style={{ left: `${position}%` }}
          />
        )}
      </div>
      <div className="relative h-3 font-mono text-[10px] opacity-80">
        {[0, low, high, 100].map((mark) => (
          <span key={mark} className="absolute -translate-x-1/2" style={{ left: `${mark}%` }}>
            {mark}
          </span>
        ))}
      </div>
      <span className="text-[11px]">{value === null ? "Sem leitura hoje." : `Hoje: ${displayNumber(value, 1)}`}</span>
    </div>
  );
}
