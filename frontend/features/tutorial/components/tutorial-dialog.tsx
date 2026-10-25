import { ArrowLeft, ArrowRight, GraduationCap, X } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { Dialog, DialogClose, DialogContent, DialogDescription, DialogTitle } from "@/shared/components/ui/dialog";
import { useSimulation } from "@/shared/hooks/useSimulation";
import { useTutorial } from "@/shared/hooks/useTutorial";
import { findTopic, topicList } from "../lib/topics";
import { MatchPause, MatchStatus, MatchSubtitle } from "./match-status";
import { TopicList } from "./topic-list";
import { TopicView } from "./topic-view";

/** Janela "Como jogar": a lista de tópicos à esquerda e o tópico aberto à direita. */
export function TutorialDialog() {
  const { isOpen, close, topicId, origin, unseenCount, select } = useTutorial();
  const { simulationActive } = useSimulation();

  const topic = findTopic(topicId);
  const index = topicList.findIndex((item) => item.id === topicId);
  const previous = topicList[index - 1];
  const next = topicList[index + 1];

  const summary =
    unseenCount > 0
      ? `${topicList.length} tópicos · ${unseenCount} para ver`
      : `${topicList.length} tópicos · todos vistos`;

  return (
    <>
      {isOpen && simulationActive && <MatchPause />}

      <Dialog open={isOpen} onOpenChange={(open) => !open && close()}>
        <DialogContent
          flush
          showCloseButton={false}
          className="flex h-205 max-h-[calc(100dvh-5rem)] w-330 max-w-[calc(100vw-7.5rem)] flex-col overflow-hidden sm:max-w-330"
        >
          {/* Cabeçalho */}
          <div className="flex items-center gap-3 border-b px-5 py-4">
            <span className="inline-flex size-9 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <GraduationCap className="size-4.5" />
            </span>
            <div className="grid">
              <DialogTitle>Como jogar</DialogTitle>
              <DialogDescription>
                {origin ? `Aberto pela dica de ${origin}` : simulationActive ? <MatchSubtitle /> : summary}
              </DialogDescription>
            </div>
            <div className="ml-auto flex items-center gap-3">
              {simulationActive && <MatchStatus />}
              <DialogClose render={<Button variant="ghost" size="icon-sm" aria-label="Fechar" />}>
                <X />
              </DialogClose>
            </div>
          </div>

          {/* Lista e tópico */}
          <div className="flex min-h-0 flex-1">
            <TopicList />
            <div className="min-w-0 flex-1 overflow-y-auto">
              <TopicView key={topic.id} topic={topic} />
            </div>
          </div>

          {/* Rodapé */}
          <div className="flex items-center justify-between border-t bg-subtle px-7 py-3.5">
            {previous ? (
              <Button variant="ghost" size="sm" onClick={() => select(previous.id)}>
                <ArrowLeft />
                {previous.title}
              </Button>
            ) : (
              <span />
            )}
            {next && (
              <Button size="sm" onClick={() => select(next.id)}>
                Próximo: {next.title}
                <ArrowRight />
              </Button>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
