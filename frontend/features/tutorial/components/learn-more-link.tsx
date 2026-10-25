import { ArrowRight, GraduationCap } from "lucide-react";
import { useContext } from "react";
import { PageLabelContext } from "@/shared/context/page-label";
import { useTutorial } from "../hooks/useTutorial";
import type { TopicId } from "../lib/topics";

/** Rodapé da dica de uma métrica: abre o tópico do Como jogar que a explica por inteiro. */
export function LearnMoreLink({ topic }: { topic: TopicId }) {
  const { open } = useTutorial();
  const label = useContext(PageLabelContext)?.label;

  return (
    <button
      type="button"
      className="mt-2 flex w-full items-center gap-1.5 border-t pt-2 font-semibold text-primary hover:text-primary-hover"
      onClick={() => open(topic, label ?? undefined)}
    >
      <GraduationCap className="size-3.5" />
      Saiba mais no Como jogar
      <ArrowRight className="size-3" />
    </button>
  );
}
