import { useRef } from "react";
import { GraduationCap } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { useTutorial } from "@/shared/hooks/useTutorial";
import { TutorialNudge } from "./tutorial-nudge";

/** Chapéu na topbar (acesso "Botão na topbar"): o ponto azul diz que ainda há tópico para ver. */
export function TopbarTutorialButton() {
  const { state, unseenCount, open } = useTutorial();
  const anchor = useRef<HTMLSpanElement>(null);

  if (state.style !== "topbar-button") return null;

  return (
    <>
      <span ref={anchor} className="relative">
        <Button variant="info-outline" size="icon" aria-label="Como jogar" onClick={() => open()}>
          <GraduationCap />
        </Button>
        {unseenCount > 0 && (
          <span
            aria-label="Há tópicos para ver"
            className="absolute -top-0.75 -right-0.75 size-2.5 rounded-full bg-primary ring-2 ring-card"
          />
        )}
      </span>
      <TutorialNudge style="topbar-button" anchor={anchor} side="bottom" />
    </>
  );
}
