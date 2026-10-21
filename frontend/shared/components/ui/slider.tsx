"use client";

import { Slider as SliderPrimitive } from "@base-ui/react/slider";
import { cn } from "@/shared/lib/utils";

type SliderProps = Omit<SliderPrimitive.Root.Props<number>, "value" | "defaultValue" | "onValueChange"> & {
  value: number;
  onValueChange: (value: number) => void;
  /** Nome do controle para leitores de tela */
  "aria-label": string;
};

/** Controle deslizante de um só valor: a trilha preenche do mínimo até a posição escolhida. */
function Slider({ className, value, onValueChange, "aria-label": ariaLabel, ...props }: SliderProps) {
  return (
    <SliderPrimitive.Root
      data-slot="slider"
      value={value}
      onValueChange={(next) => onValueChange(Array.isArray(next) ? next[0] : next)}
      className={cn("w-full data-disabled:opacity-60", className)}
      {...props}
    >
      <SliderPrimitive.Control data-slot="slider-control" className="flex h-5 w-full items-center select-none">
        <SliderPrimitive.Track data-slot="slider-track" className="relative h-1.5 w-full rounded-full bg-muted">
          <SliderPrimitive.Indicator
            data-slot="slider-range"
            className="rounded-full bg-primary data-disabled:bg-faint-foreground"
          />
          <SliderPrimitive.Thumb
            data-slot="slider-thumb"
            getAriaLabel={() => ariaLabel}
            className="size-4.5 rounded-full border-2 border-primary bg-background shadow-sm transition-shadow outline-none has-focus-visible:ring-4 has-focus-visible:ring-ring/30 data-disabled:border-faint-foreground data-dragging:ring-4 data-dragging:ring-ring/30"
          />
        </SliderPrimitive.Track>
      </SliderPrimitive.Control>
    </SliderPrimitive.Root>
  );
}

export { Slider };
