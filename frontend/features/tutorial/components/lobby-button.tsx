import { GraduationCap } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { useTutorial } from "../hooks/useTutorial";

/** Botão do lobby: contorno azul e contador azul até a primeira abertura, contador cinza depois, sem contador com tudo visto. */
export function LobbyTutorialButton({ className }: { className?: string }) {
  const { state, unseenCount, open } = useTutorial();

  return (
    <Button variant={state.opened ? "outline" : "outline-highlight"} className={className} onClick={() => open()}>
      <GraduationCap />
      Como jogar
      {unseenCount > 0 && (
        <Badge variant={state.opened ? "secondary" : "default"} size="sm" numeric>
          {unseenCount}
        </Badge>
      )}
    </Button>
  );
}
