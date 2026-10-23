import { Slider } from "@/shared/components/ui/slider";
import { cn } from "@/shared/lib/utils";

type Mark = { value: number; label: string };

type MarkedSliderProps = {
  value: number;
  onValueChange: (value: number) => void;
  min: number;
  max: number;
  step: number;
  marks: Mark[];
  disabled?: boolean;
  "aria-label": string;
};

const percentOf = (value: number, min: number, max: number) => ((value - min) / (max - min)) * 100;

/** Slider com as marcas de referência embaixo; a mais próxima do valor aparece em destaque. */
export function MarkedSlider({ value, onValueChange, min, max, step, marks, disabled, "aria-label": ariaLabel }: MarkedSliderProps) {
  const nearest = marks.reduce((best, mark) => (Math.abs(mark.value - value) < Math.abs(best.value - value) ? mark : best));

  return (
    <div className="grid gap-1.5">
      <Slider
        aria-label={ariaLabel}
        value={value}
        onValueChange={onValueChange}
        min={min}
        max={max}
        step={step}
        disabled={disabled}
      />
      <div className="relative h-4">
        {marks.map((mark, index) => {
          const position = percentOf(mark.value, min, max);
          const first = index === 0;
          const last = index === marks.length - 1;
          return (
            <span
              key={mark.value}
              className={cn(
                "absolute text-[11px] whitespace-nowrap text-faint-foreground",
                !first && !last && "-translate-x-1/2",
                mark === nearest && "font-semibold text-foreground",
              )}
              style={first ? { left: 0 } : last ? { right: 0 } : { left: `${position}%` }}
            >
              {mark.label}
            </span>
          );
        })}
      </div>
    </div>
  );
}
