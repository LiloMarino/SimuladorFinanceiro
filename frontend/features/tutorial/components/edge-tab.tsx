import { useRef } from "react";
import { ChevronLeft, ChevronRight, GraduationCap } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { useTutorial } from "../hooks/useTutorial";
import { TutorialNudge } from "./tutorial-nudge";

/** Aba na borda direita da tela (acesso "Aba na borda"): abre o Como jogar e pode recolher em alça. */
export function EdgeTab() {
  const { state, unseenCount, open, setCollapsed } = useTutorial();
  const anchor = useRef<HTMLDivElement>(null);

  if (state.style !== "edge-tab") return null;

  return (
    <>
      <div ref={anchor} className="fixed top-75 right-0 z-40">
        {state.collapsed ? (
          <button
            type="button"
            aria-label="Mostrar a aba Como jogar"
            className="flex h-13 w-3.5 items-center justify-center rounded-l-md bg-primary text-primary-foreground"
            onClick={() => setCollapsed(false)}
          >
            <ChevronLeft className="size-2.5" />
          </button>
        ) : (
          <div className="flex w-11 flex-col items-center rounded-l-xl bg-primary py-3 text-primary-foreground shadow-lg">
            <button type="button" className="flex flex-col items-center gap-2.5" onClick={() => open()}>
              <GraduationCap className="size-4.5" />
              <span className="rotate-180 text-[13px] font-semibold tracking-tight [writing-mode:vertical-rl]">
                Como jogar
              </span>
              {unseenCount > 0 && (
                <Badge variant="on-primary" size="sm" numeric>
                  {unseenCount}
                </Badge>
              )}
            </button>
            <button
              type="button"
              aria-label="Recolher a aba Como jogar"
              className="mt-2.5 text-primary-foreground/70 hover:text-primary-foreground"
              onClick={() => setCollapsed(true)}
            >
              <ChevronRight className="size-3.5" />
            </button>
          </div>
        )}
      </div>
      <TutorialNudge style="edge-tab" anchor={anchor} side="left" />
    </>
  );
}
