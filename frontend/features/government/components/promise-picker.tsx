import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { cn } from "@/shared/lib/utils";
import { PROMISE_BANDS, PROMISE_ENDS, promiseBand, rulerPosition } from "../lib/election";

type PromisePickerProps = {
  value: number;
  onChange: (value: number) => void;
  disabled?: boolean;
};

/** A régua da promessa para escolher: cinco faixas clicáveis, com o que a faixa escolhida quer dizer. */
export function PromisePicker({ value, onChange, disabled }: PromisePickerProps) {
  const band = promiseBand(value);

  return (
    <div className="grid gap-2">
      <div className="w-full">
        <div role="radiogroup" aria-label="Promessa do partido" className="relative h-6">
          <span className="absolute inset-x-0 top-1/2 h-1.5 -translate-y-1/2 rounded-full bg-linear-to-r from-info-soft via-muted to-warning-soft" />
          {PROMISE_BANDS.map((option) => (
            <button
              key={option.value}
              type="button"
              role="radio"
              aria-checked={option.value === value}
              aria-label={`Faixa ${option.value}: ${option.title}`}
              disabled={disabled}
              onClick={() => onChange(option.value)}
              className={cn(
                "absolute top-1/2 size-4.5 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 bg-card shadow-sm transition-colors outline-none focus-visible:ring-3 focus-visible:ring-ring/50 disabled:opacity-50",
                option.value === value ? "size-5 border-primary bg-primary" : "border-border hover:border-primary",
              )}
              style={{ left: `${rulerPosition(option.value)}%` }}
            />
          ))}
        </div>
        <div className="mt-1 flex justify-between text-[11px] text-muted-foreground">
          <span>{PROMISE_ENDS.low}</span>
          <span>{PROMISE_ENDS.high}</span>
        </div>
      </div>
      <Alert variant="info">
        <AlertTitle>
          Faixa {band.value} · {band.title}
        </AlertTitle>
        <AlertDescription>{band.description}</AlertDescription>
      </Alert>
    </div>
  );
}
