import type { RefObject } from "react";
import { useLocation } from "react-router-dom";
import { GraduationCap, X } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { Popover, PopoverContent } from "@/shared/components/ui/popover";
import { useTutorial } from "../hooks/useTutorial";
import { topicList } from "../lib/topics";
import { nudgeTopicFor } from "../lib/tutorial-progress";
import type { TutorialStyle } from "../lib/tutorial-storage";

interface TutorialNudgeProps {
  /** O acesso a que o aviso pertence: só o escolhido pelo jogador mostra o aviso. */
  style: TutorialStyle;
  anchor: RefObject<HTMLElement | null>;
  side: "left" | "right" | "bottom";
}

/** Aviso que oferece o primeiro tópico da tela que o jogador ainda não viu, uma única vez por tópico. */
export function TutorialNudge({ style, anchor, side }: TutorialNudgeProps) {
  const { state, isOpen, open, answerNudge } = useTutorial();
  const { pathname } = useLocation();

  const topic = state.style === style && !isOpen ? nudgeTopicFor(state, topicList, pathname) : undefined;
  if (!topic) return null;

  return (
    <Popover open>
      <PopoverContent
        anchor={anchor}
        side={side}
        sideOffset={12}
        initialFocus={false}
        role="dialog"
        aria-label="Tópico sobre esta tela"
        variant="flush"
        className="w-80"
      >
        <div className="grid gap-2.5 p-4">
          <div className="flex items-center gap-2">
            <span className="inline-flex size-7 items-center justify-center rounded-lg bg-info-soft text-primary">
              <GraduationCap className="size-4" />
            </span>
            <span className="text-[11px] font-semibold tracking-wider text-info uppercase">Tópico sobre esta tela</span>
            <Button
              variant="ghost"
              size="icon-xs"
              className="ml-auto"
              aria-label="Dispensar o aviso"
              onClick={() => answerNudge(topic.id)}
            >
              <X />
            </Button>
          </div>
          <div className="grid gap-0.5">
            <b>{topic.title}</b>
            <span className="text-[13px] text-muted-foreground">
              {topic.summary} {topic.minutes} min.
            </span>
          </div>
          <div className="flex gap-2">
            <Button
              size="sm"
              onClick={() => {
                answerNudge(topic.id);
                open(topic.id);
              }}
            >
              Ver tópico
            </Button>
            <Button variant="ghost" size="sm" onClick={() => answerNudge(topic.id)}>
              Agora não
            </Button>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}
