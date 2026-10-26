"use client";

import { useRef, type PointerEvent, type ReactNode } from "react";
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

type RangeBarDrag = {
  /** Passos inteiros que a barra andou desde que foi pressionada */
  steps: number;
  phase: "start" | "move" | "end";
};

type RangeSliderProps = Omit<
  SliderPrimitive.Root.Props<readonly number[]>,
  "value" | "defaultValue" | "onValueChange" | "onValueCommitted" | "children" | "aria-label"
> & {
  value: readonly [number, number];
  onValueChange: (value: [number, number]) => void;
  onValueCommitted?: () => void;
  /** Arrasto da barra entre as alças; quem usa soma os passos às duas pontas */
  onBarDrag?: (drag: RangeBarDrag) => void;
  /** Nome de cada alça para leitores de tela: início e fim */
  thumbLabels: readonly [string, string];
  getThumbValueText?: (value: number, index: number) => string;
  /** Pintura da trilha atrás da barra: faixas de cor */
  track?: ReactNode;
  /** Camada sobre a trilha, na mesma caixa dela: marcadores e rótulos */
  children?: ReactNode;
};

/** Barra entre as alças: arrastá-la desloca a faixa inteira, sem mexer na alça mais próxima. */
function RangeBar({
  onDrag,
  disabled,
  span,
}: {
  onDrag?: (drag: RangeBarDrag) => void;
  disabled?: boolean;
  span: number;
}) {
  const gesture = useRef<{ originX: number; pxPerStep: number } | null>(null);
  const draggable = !disabled && onDrag !== undefined;

  const stepsOf = (event: PointerEvent<HTMLDivElement>) =>
    Math.round((event.clientX - (gesture.current?.originX ?? 0)) / (gesture.current?.pxPerStep ?? 1));

  return (
    <SliderPrimitive.Indicator
      data-slot="range-slider-bar"
      className={cn(
        "relative top-px h-3 touch-none rounded-md bg-primary data-disabled:bg-faint-foreground",
        draggable && "cursor-grab active:cursor-grabbing active:bg-primary-hover active:ring-4 active:ring-ring/20",
      )}
      onPointerDown={(event: PointerEvent<HTMLDivElement>) => {
        if (!draggable || event.button !== 0) return;
        // O gesto é da barra: o controle não chega a mover a alça mais próxima
        event.stopPropagation();
        const bar = event.currentTarget;
        bar.setPointerCapture(event.pointerId);
        const track = bar.parentElement as HTMLElement;
        gesture.current = { originX: event.clientX, pxPerStep: track.getBoundingClientRect().width / span };
        onDrag({ steps: 0, phase: "start" });
      }}
      onPointerMove={(event: PointerEvent<HTMLDivElement>) => {
        if (gesture.current) onDrag?.({ steps: stepsOf(event), phase: "move" });
      }}
      onPointerUp={(event: PointerEvent<HTMLDivElement>) => {
        if (!gesture.current) return;
        onDrag?.({ steps: stepsOf(event), phase: "end" });
        gesture.current = null;
      }}
      onPointerCancel={() => {
        if (!gesture.current) return;
        gesture.current = null;
        onDrag?.({ steps: 0, phase: "end" });
      }}
    >
      <span className="pointer-events-none flex h-full items-center justify-center gap-[3px]">
        {[0, 1, 2].map((dot) => (
          <i key={dot} className="h-2 w-0.5 rounded-[1px] bg-primary-foreground/75" />
        ))}
      </span>
    </SliderPrimitive.Indicator>
  );
}

/** Controle deslizante de faixa: duas alças e a barra entre elas, que também se arrasta. */
function RangeSlider({
  className,
  value,
  onValueChange,
  onValueCommitted,
  onBarDrag,
  thumbLabels,
  getThumbValueText,
  track,
  children,
  min = 0,
  max = 100,
  ...props
}: RangeSliderProps) {
  return (
    <SliderPrimitive.Root
      data-slot="range-slider"
      value={value}
      min={min}
      max={max}
      minStepsBetweenValues={1}
      thumbCollisionBehavior="none"
      onValueChange={(next) => onValueChange([next[0], next[1]])}
      onValueCommitted={() => onValueCommitted?.()}
      className={cn("w-full data-disabled:opacity-60", className)}
      {...props}
    >
      <SliderPrimitive.Control data-slot="range-slider-control" className="relative h-3.5 w-full select-none">
        <SliderPrimitive.Track data-slot="range-slider-track" className="relative h-full w-full rounded-full">
          {track}
          <RangeBar onDrag={onBarDrag} disabled={props.disabled} span={max - min} />
          {([0, 1] as const).map((index) => (
            <SliderPrimitive.Thumb
              key={index}
              index={index}
              data-slot="range-slider-thumb"
              getAriaLabel={() => thumbLabels[index]}
              getAriaValueText={getThumbValueText && ((_, thumbValue) => getThumbValueText(thumbValue, index))}
              className="z-10 size-5 rounded-full border-2 border-primary bg-card shadow-sm transition-shadow outline-none has-focus-visible:ring-4 has-focus-visible:ring-ring/30 data-disabled:border-input data-disabled:bg-muted data-disabled:shadow-none data-dragging:ring-4 data-dragging:ring-ring/30"
            />
          ))}
        </SliderPrimitive.Track>
        {children}
      </SliderPrimitive.Control>
    </SliderPrimitive.Root>
  );
}

export { Slider, RangeSlider };
export type { RangeBarDrag };
