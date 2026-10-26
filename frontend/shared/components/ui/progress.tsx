"use client";

import type { CSSProperties, ReactNode } from "react";
import { Progress as ProgressPrimitive } from "@base-ui/react/progress";
import { type VariantProps } from "class-variance-authority";
import { cn } from "@/shared/lib/utils";
import { progressIndicatorVariants, progressTrackVariants } from "./variants/progressVariants";

type ProgressProps = ProgressPrimitive.Root.Props &
  VariantProps<typeof progressTrackVariants> & {
    /** Tom do preenchimento; o padrão acompanha o tom da trilha */
    indicatorTone?: VariantProps<typeof progressIndicatorVariants>["tone"];
    /** Cor própria do preenchimento (valor CSS), para barras na cor de um jogador */
    color?: string | undefined;
    /** `ProgressMarker`s e `ProgressEndMark`, desenhados sobre a trilha da variante `markers` */
    markers?: ReactNode;
  };

function Progress({
  className,
  children,
  value,
  variant,
  size,
  tone,
  indicatorTone,
  color,
  markers,
  ...props
}: ProgressProps) {
  return (
    <ProgressPrimitive.Root
      value={value}
      data-slot="progress"
      className={cn("flex flex-wrap gap-3", className)}
      {...props}
    >
      {children}
      <ProgressTrack variant={variant} size={size} tone={tone}>
        <ProgressIndicator tone={indicatorTone ?? (tone === "inverse" ? "inverse" : "default")} color={color} />
        {markers}
      </ProgressTrack>
    </ProgressPrimitive.Root>
  );
}

function ProgressTrack({
  className,
  variant,
  size,
  tone,
  ...props
}: ProgressPrimitive.Track.Props & VariantProps<typeof progressTrackVariants>) {
  return (
    <ProgressPrimitive.Track
      className={cn(progressTrackVariants({ variant, size, tone }), className)}
      data-slot="progress-track"
      {...props}
    />
  );
}

function ProgressIndicator({
  className,
  tone,
  color,
  style,
  ...props
}: Omit<ProgressPrimitive.Indicator.Props, "style"> &
  VariantProps<typeof progressIndicatorVariants> & { color?: string | undefined; style?: CSSProperties }) {
  return (
    <ProgressPrimitive.Indicator
      data-slot="progress-indicator"
      className={cn(progressIndicatorVariants({ tone }), className)}
      style={color ? { ...style, backgroundColor: color } : style}
      {...props}
    />
  );
}

type ProgressMarkerProps = {
  /** Posição na trilha, de 0 (início) a 1 (meta) */
  position: number;
  /** Fundo do marcador (valor CSS) e cor do conteúdo */
  color: string;
  foreground: string;
  /** O marcador de quem vê a tela: maior e com anel */
  highlighted?: boolean;
  title: string;
  children: ReactNode;
};

/** Marcador sobre a trilha (variante `markers`): a sigla de um jogador ou o escudo de uma equipe. */
function ProgressMarker({ position, color, foreground, highlighted, title, children }: ProgressMarkerProps) {
  const clamped = Math.min(Math.max(position, 0), 1);
  return (
    <span
      data-slot="progress-marker"
      title={title}
      className={cn(
        "absolute top-1/2 inline-flex -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full text-[9px] font-bold tracking-[.02em] shadow-[0_0_0_2px_var(--card)] [&_svg]:size-3",
        highlighted ? "z-10 size-6.5 text-[10px] shadow-[0_0_0_2px_var(--card),0_0_0_4px_var(--primary)]" : "size-5.5",
      )}
      style={{ left: `${clamped * 100}%`, backgroundColor: color, color: foreground }}
    >
      {children}
    </span>
  );
}

/** Traço no fim da trilha: onde fica a meta. */
function ProgressEndMark() {
  return (
    <span
      data-slot="progress-end-mark"
      aria-hidden="true"
      className="absolute top-1/2 -right-0.5 h-4.5 w-0.5 -translate-y-1/2 rounded-[1px] bg-foreground"
    />
  );
}

/** Trecho listrado da trilha (variante `default`): a parte do caminho que é mercado gerado. */
function ProgressGenerated({ from, to }: { from: number; to: number }) {
  return (
    <span
      data-slot="progress-generated"
      aria-hidden="true"
      className="absolute inset-y-0 bg-generated"
      style={{ left: `${from * 100}%`, width: `${Math.max(to - from, 0) * 100}%` }}
    />
  );
}

function ProgressLabel({ className, ...props }: ProgressPrimitive.Label.Props) {
  return (
    <ProgressPrimitive.Label className={cn("text-sm font-medium", className)} data-slot="progress-label" {...props} />
  );
}

function ProgressValue({ className, ...props }: ProgressPrimitive.Value.Props) {
  return (
    <ProgressPrimitive.Value
      className={cn("ml-auto text-sm text-muted-foreground tabular-nums", className)}
      data-slot="progress-value"
      {...props}
    />
  );
}

export {
  Progress,
  ProgressTrack,
  ProgressIndicator,
  ProgressEndMark,
  ProgressGenerated,
  ProgressLabel,
  ProgressMarker,
  ProgressValue,
};
