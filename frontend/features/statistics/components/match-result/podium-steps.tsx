import type { CSSProperties, ReactNode } from "react";
import { cn } from "@/shared/lib/utils";

// Degraus na ordem visual: 2º à esquerda, 1º no meio e mais alto, 3º à direita
const STEPS = [
  { position: 2, height: "h-[110px]" },
  { position: 1, height: "h-[150px]" },
  { position: 3, height: "h-20" },
] as const;

interface PodiumStepsProps<T extends { position: number }> {
  items: T[];
  emptyLabel: (position: number) => string;
  renderEntry: (item: T, first: boolean) => ReactNode;
  stepClassName: (item: T | undefined, first: boolean) => string;
  columnStyle?: (item: T) => CSSProperties;
}

/** Os três degraus do pódio; cada lista de colocados traz o conteúdo da coluna e a cor do degrau. */
export function PodiumSteps<T extends { position: number }>({
  items,
  emptyLabel,
  renderEntry,
  stepClassName,
  columnStyle,
}: PodiumStepsProps<T>) {
  const byPosition = new Map(items.map((item) => [item.position, item]));

  return (
    <div className="flex w-full max-w-[480px] items-end gap-3">
      {STEPS.map((step) => {
        const item = byPosition.get(step.position);
        const first = step.position === 1;
        return (
          <div
            key={step.position}
            className="flex flex-1 flex-col items-center gap-2"
            style={item && columnStyle ? columnStyle(item) : undefined}
          >
            {item ? renderEntry(item, first) : <span className="text-sidebar-muted">{emptyLabel(step.position)}</span>}
            <div className={cn("flex w-full justify-center rounded-t-[10px] pt-2.5", step.height, stepClassName(item, first))}>
              <span className="font-mono text-[22px] font-semibold text-white">{step.position}º</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
