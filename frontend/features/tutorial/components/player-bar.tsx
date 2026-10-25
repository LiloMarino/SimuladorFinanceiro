import { Pause, Play } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { cn } from "@/shared/lib/utils";
import type { Player } from "../hooks/usePlayer";
import type { HowToTopic } from "../lib/topics";

/** Barra de reprodução: pausa, um segmento por passo (clicável) e a posição. */
export function PlayerBar({ topic, player }: { topic: HowToTopic; player: Player }) {
  return (
    <div className="absolute inset-x-3 bottom-3 z-30 flex items-center gap-2.5 rounded-lg bg-card/90 px-2.5 py-1.5 ring-1 ring-border">
      <Button
        variant="dark"
        size="icon-xs"
        aria-label={player.playing ? "Pausar a animação" : "Tocar a animação"}
        onClick={player.toggle}
      >
        {player.playing ? <Pause /> : <Play />}
      </Button>
      <div className="flex flex-1 gap-1">
        {topic.steps.map((text, index) => (
          <button
            key={text}
            type="button"
            aria-label={`Ir para o passo ${index + 1}`}
            aria-current={index === player.step ? "step" : undefined}
            className="group/segment flex-1 py-2"
            onClick={() => player.jumpToStep(index)}
          >
            <span
              className={cn(
                "block h-1 rounded-sm transition-colors group-hover/segment:bg-primary/60",
                index <= player.step ? "bg-primary" : "bg-border",
              )}
            />
          </button>
        ))}
      </div>
      <span className="font-mono text-xs text-muted-foreground">
        Passo {player.step + 1} de {topic.steps.length}
      </span>
    </div>
  );
}
