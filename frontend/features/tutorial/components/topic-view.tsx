import { Fragment } from "react";
import { Lightbulb } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { cn } from "@/shared/lib/utils";
import { usePlayer } from "../hooks/usePlayer";
import type { ConceptTopic, HowToTopic, Topic } from "../lib/topics";
import { PlayerBar } from "./player-bar";
import { TopicIllustration } from "./topic-illustration";

/** `**trecho**` vira negrito. */
function RichText({ text }: { text: string }) {
  return text
    .split("**")
    .map((part, index) => (index % 2 ? <b key={index}>{part}</b> : <Fragment key={index}>{part}</Fragment>));
}

export function TopicView({ topic }: { topic: Topic }) {
  return topic.kind === "howto" ? <HowToView topic={topic} /> : <ConceptView topic={topic} />;
}

function HowToView({ topic }: { topic: HowToTopic }) {
  const player = usePlayer(topic);

  return (
    <div className="grid grid-cols-[minmax(0,1.35fr)_minmax(0,1fr)] content-start gap-7 px-7 py-6">
      {/* Animação */}
      <TopicIllustration
        topic={topic}
        beat={player.beat}
        step={player.step}
        controls={<PlayerBar topic={topic} player={player} />}
      />

      {/* Texto */}
      <div className="grid content-start gap-4">
        <div className="grid gap-1.5">
          <span className="text-[11px] font-semibold tracking-wider text-faint-foreground uppercase">
            Como se joga · {topic.minutes} min
          </span>
          <h2 className="text-[22px] font-bold">{topic.title}</h2>
          <p className="text-muted-foreground">{topic.intro}</p>
        </div>

        {/* Passos */}
        <ol className="grid gap-1">
          {topic.steps.map((text, index) => (
            <li key={text}>
              <button
                type="button"
                aria-current={index === player.step ? "step" : undefined}
                className="grid w-full grid-cols-[28px_1fr] items-start gap-2.5 rounded-lg p-1 text-left hover:bg-muted/60"
                onClick={() => player.jumpToStep(index)}
              >
                <b
                  className={cn(
                    "inline-flex size-7 items-center justify-center rounded-full text-[13px]",
                    index === player.step ? "bg-primary text-primary-foreground" : "bg-secondary",
                  )}
                >
                  {index + 1}
                </b>
                <span className="pt-1">
                  <RichText text={text} />
                </span>
              </button>
            </li>
          ))}
        </ol>

        {/* Dica */}
        <Alert variant="info">
          <Lightbulb />
          <AlertTitle>Dica</AlertTitle>
          <AlertDescription>{topic.tip}</AlertDescription>
        </Alert>
      </div>
    </div>
  );
}

function ConceptView({ topic }: { topic: ConceptTopic }) {
  return (
    <div className="grid max-w-2xl content-start gap-3.5 px-7 py-6">
      <div className="grid gap-1">
        <span className="text-[11px] font-semibold tracking-wider text-faint-foreground uppercase">
          Conceitos · {topic.minutes} min
        </span>
        <h2 className="text-[19px] font-bold">{topic.title}</h2>
      </div>

      {/* Ilustração com os números do exemplo */}
      <TopicIllustration topic={topic} beat={0} step={0} />

      <p className="text-[13px]">
        <RichText text={topic.body} />
      </p>

      <Alert variant="muted">
        <AlertTitle>{topic.callout.title}</AlertTitle>
        <AlertDescription>{topic.callout.text}</AlertDescription>
      </Alert>
    </div>
  );
}
