import type { CSSProperties, ReactNode } from "react";
import { Link as LinkIcon, Megaphone, Zap } from "lucide-react";
import type { TimelineMilestone } from "@/types";

type Kind = TimelineMilestone["kind"];

const ICONS = { PROMISE: Megaphone, CAMPAIGN: Zap, ALLIANCE: LinkIcon } as const;

// Promessa e ação usam a cor do partido; aliança é âmbar, com a cor do partido na metade de baixo
function glyphStyle(kind: Kind, color: string): CSSProperties {
  if (kind === "ALLIANCE") {
    return {
      background: `linear-gradient(135deg, var(--warning-soft) 50%, color-mix(in srgb, ${color} 12%, var(--card)) 50%)`,
      borderColor: "color-mix(in srgb, var(--warning) 45%, var(--card))",
      color: "var(--warning)",
    };
  }
  return {
    background: `color-mix(in srgb, ${color} 12%, var(--card))`,
    borderColor: `color-mix(in srgb, ${color} 30%, var(--card))`,
    color,
  };
}

type MapMilestoneGlyphProps = {
  kind: Kind;
  color: string;
  /** O selo de contagem no canto: quantos itens o marco junta. */
  count?: number | null;
  children?: ReactNode;
};

/** O quadradinho de um marco: o ícone do tipo na cor do partido e, quando junta vários, o selo com o número. */
export function MapMilestoneGlyph({ kind, color, count = null, children }: MapMilestoneGlyphProps) {
  const Icon = ICONS[kind];
  return (
    <span
      className="relative inline-flex size-6 items-center justify-center rounded-md border"
      style={glyphStyle(kind, color)}
    >
      <Icon className="size-3.5" aria-hidden />
      {count !== null && (
        <span className="absolute -top-1.5 -right-0.5 flex h-3.75 min-w-3.75 items-center justify-center rounded-full bg-foreground px-0.75 font-mono text-xs leading-none font-bold text-background">
          {count}
        </span>
      )}
      {children}
    </span>
  );
}
