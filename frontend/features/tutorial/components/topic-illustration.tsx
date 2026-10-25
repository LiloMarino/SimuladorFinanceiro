import {
  createElement,
  lazy,
  Suspense,
  useState,
  type ComponentType,
  type LazyExoticComponent,
  type ReactNode,
} from "react";
import { TriangleAlert } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { cn } from "@/shared/lib/utils";
import type { IllustrationProps, Topic } from "../lib/topics";
import { IllustrationBoundary } from "./illustration-boundary";

type Illustration = LazyExoticComponent<ComponentType<IllustrationProps>>;

// Uma ilustração lazy por tópico e tentativa: "Tentar de novo" pede um import novo
const illustrations = new Map<string, Illustration>();

function illustrationFor(topic: Topic, attempt: number) {
  const key = `${topic.id}:${attempt}`;
  let illustration = illustrations.get(key);
  if (!illustration) {
    illustration = lazy(topic.loadIllustration);
    illustrations.set(key, illustration);
  }
  return illustration;
}

interface TopicIllustrationProps {
  topic: Topic;
  beat: number;
  step: number;
  /** Controles de reprodução, sobre a base da ilustração. */
  controls?: ReactNode;
}

/** Quadro da ilustração: a cena carrega à parte e, se falhar, a imagem parada fica no lugar. */
export function TopicIllustration({ topic, beat, step, controls }: TopicIllustrationProps) {
  const [attempt, setAttempt] = useState(0);

  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-xl border bg-background",
        topic.kind === "howto" ? "h-140" : "h-60",
      )}
    >
      <IllustrationBoundary
        key={attempt}
        fallback={<StillFrame topic={topic} attempt={attempt} onRetry={() => setAttempt(attempt + 1)} />}
      >
        <Suspense fallback={<IllustrationSkeleton />}>
          <IllustrationSlot topic={topic} attempt={attempt} beat={beat} step={step} />
        </Suspense>
      </IllustrationBoundary>
      {controls}
    </div>
  );
}

/** A imagem do trecho-pôster, sem cursor nem marcador, com o aviso e a nova tentativa. */
function StillFrame({ topic, attempt, onRetry }: { topic: Topic; attempt: number; onRetry: () => void }) {
  const poster = topic.kind === "howto" ? topic.poster : 0;
  const step = topic.kind === "howto" ? topic.beats[poster].step : 0;

  return (
    <>
      {/* Imagem parada */}
      <IllustrationBoundary fallback={null}>
        <Suspense fallback={null}>
          <IllustrationSlot topic={topic} attempt={attempt} beat={poster} step={step} still />
        </Suspense>
      </IllustrationBoundary>

      {/* Aviso */}
      <Alert variant="warning" className="absolute inset-x-3 bottom-3 z-40 w-auto">
        <TriangleAlert />
        <AlertTitle>A animação não carregou</AlertTitle>
        <AlertDescription>
          <div className="flex items-center justify-between gap-2">
            Ficou a imagem parada.
            <Button variant="outline" size="xs" onClick={onRetry}>
              Tentar de novo
            </Button>
          </div>
        </AlertDescription>
      </Alert>
    </>
  );
}

/** A ilustração lazy da tentativa em curso, com as props da cena. */
function IllustrationSlot({ topic, attempt, ...scene }: IllustrationProps & { topic: Topic; attempt: number }) {
  return createElement(illustrationFor(topic, attempt), scene);
}

function IllustrationSkeleton() {
  return (
    <div className="absolute inset-0 grid place-items-center" aria-busy="true" aria-label="Carregando a animação">
      <div className="grid w-75 gap-2.5">
        <Skeleton className="h-4.5 w-[60%]" />
        <Skeleton className="h-4.5" />
        <Skeleton className="h-4.5" />
        <Skeleton className="h-4.5 w-[80%]" />
      </div>
    </div>
  );
}
