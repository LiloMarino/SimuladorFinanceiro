import { CalendarDays, ChevronLeft, ChevronRight, History, Info, Pause, Play } from "lucide-react";
import { Alert, AlertAction } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Kbd } from "@/shared/components/ui/kbd";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { CardState } from "@/shared/components/card-state";
import { partyColor } from "@/shared/lib/party-colors";
import type ApiError from "@/shared/lib/models/ApiError";
import type { ElectionTimeline, MapPlace, TimelinePoint } from "@/types";
import type { useTimelinePlayback } from "../hooks/useTimelinePlayback";
import { flagText, fullDate } from "../lib/map-timeline";
import { MILESTONE_NAMES } from "../lib/map-milestones";
import { MapMilestoneGlyph } from "./map-milestone-glyph";
import { MapTimelineRuler } from "./map-timeline-ruler";
import { MapTimelineYears } from "./map-timeline-years";

const RULER_POINTS = 17;

type MapTimelineProps = {
  timeline: ElectionTimeline | undefined;
  error: ApiError | null;
  onRetry: () => void;
  /** O ponto escolhido na régua; vem do mesmo `timeline`. */
  selected: TimelinePoint | undefined;
  /** O ponto escolhido é o último que já aconteceu. */
  isToday: boolean;
  playback: ReturnType<typeof useTimelinePlayback>;
  /** O partido em foco nas lentes: dono das promessas e ações da faixa de marcos. */
  focusParty: number | null;
  regions: MapPlace[];
  onYear: (year: number) => void;
  onSelect: (point: TimelinePoint) => void;
  onToday: () => void;
};

// O que o ponto escolhido é, para a faixa "Você está vendo …"
function pastLabel(point: TimelinePoint) {
  switch (point.kind) {
    case "FIRST_ROUND":
      return "a apuração do 1º turno de";
    case "RUNOFF":
      return "a apuração do 2º turno de";
    default:
      return "a pesquisa de";
  }
}

function Title() {
  return (
    <span className="flex items-center gap-2">
      <History className="size-4" />
      Linha do tempo
    </span>
  );
}

function TimelineSkeleton() {
  return (
    <div className="grid gap-4.5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Skeleton className="h-4.5 w-32" />
          <Skeleton className="h-8 w-50" />
        </div>
        <Skeleton className="h-8 w-50" />
      </div>
      <div className="relative h-10 px-6.5">
        <Skeleton className="absolute inset-x-6.5 top-4.5 h-1" />
        <div className="relative flex justify-between">
          {Array.from({ length: RULER_POINTS }, (_, index) => (
            <Skeleton key={index} circle className="size-3" />
          ))}
        </div>
      </div>
      <Skeleton className="h-3.5 w-105" />
    </div>
  );
}

/** O card da linha do tempo: seletor de ano, controles de reprodução, régua do ciclo e legenda dos marcos. */
export function MapTimeline({
  timeline,
  error,
  onRetry,
  selected,
  isToday,
  playback,
  focusParty,
  regions,
  onYear,
  onSelect,
  onToday,
}: MapTimelineProps) {
  if (error || !timeline) {
    return (
      <CardState
        title={<Title />}
        label="Carregando a linha do tempo"
        error={error}
        onRetry={onRetry}
        errorTitle="Não foi possível carregar o histórico das eleições"
        errorDescription="O mapa continua mostrando o hoje. Tente de novo; se o erro voltar, recarregue a página."
      >
        <TimelineSkeleton />
      </CardState>
    );
  }

  const { years, year, points, parties } = timeline;
  const chosen = years.find((item) => item.year === year);
  const started = points.some((point) => point.happened);
  const focus = parties.find((party) => party.id === focusParty);
  const mandate = isToday && years.at(-1)?.status === "UPCOMING";

  // Antes da primeira campanha só o seletor e o aviso aparecem
  if (!started || !selected) {
    return (
      <Card>
        <CardContent>
          <div className="grid gap-3">
            <div className="flex items-center gap-3 text-[15px] font-semibold">
              <Title />
              <MapTimelineYears years={years} year={year} onChange={onYear} />
            </div>
            <div className="flex h-16 items-center justify-center gap-2 rounded-[10px] border border-dashed border-input bg-subtle px-4 text-[13px] text-muted-foreground">
              <Info className="size-4 shrink-0 text-faint-foreground" />
              {chosen
                ? `A campanha de ${chosen.year} abre em ${fullDate(chosen.opens_on)}${points[0] ? `, e a primeira pesquisa sai em ${fullDate(points[0].date)}` : ""}. Até lá, Aprovação e Onde vive cada grupo já funcionam.`
                : "A partida ainda não teve campanha."}
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <div className="grid gap-2">
          {/* Faixa do ponto passado */}
          {!isToday && (
            <Alert variant="info" className="items-center">
              <CalendarDays />
              <span className="text-[13px] text-primary">
                Você está vendo {pastLabel(selected)} <b>{fullDate(selected.date)}</b>.
              </span>
              <AlertAction>
                <Button size="sm" variant="outline" onClick={onToday}>
                  Voltar ao hoje
                </Button>
              </AlertAction>
            </Alert>
          )}

          {/* Cabeçalho */}
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <h2 className="text-[15px] font-semibold">
                <Title />
              </h2>
              <MapTimelineYears years={years} year={year} onChange={onYear} />
            </div>
            <div className="flex items-center gap-3.5">
              <span className="flex items-center gap-1.5 text-[13px] text-muted-foreground">
                <Kbd className="ml-0">←</Kbd>
                <Kbd className="ml-0">→</Kbd>
                andam a régua
              </span>
              <div className="flex items-center gap-1.5">
                <Button size="icon-sm" variant="outline" aria-label="Pesquisa anterior" onClick={playback.previous}>
                  <ChevronLeft />
                </Button>
                <Button size="sm" variant="dark" onClick={playback.toggle}>
                  {playback.playing ? <Pause /> : <Play />}
                  {playback.playing ? "Pausar" : "Reproduzir"}
                </Button>
                <Button size="icon-sm" variant="outline" aria-label="Próxima pesquisa" onClick={playback.next}>
                  <ChevronRight />
                </Button>
                {!isToday && (
                  <Button size="sm" variant="outline" onClick={onToday}>
                    Voltar ao hoje
                  </Button>
                )}
              </div>
            </div>
          </div>

          {/* Régua */}
          <MapTimelineRuler
            timeline={timeline}
            selected={selected}
            flag={flagText(selected, points, parties, mandate)}
            focusParty={focusParty}
            regions={regions}
            onSelect={onSelect}
          />

          {/* Legenda */}
          <div className="flex items-center justify-between gap-4 border-t pt-2.5 text-xs text-muted-foreground">
            <span>
              Os marcos são do partido em foco nas lentes; as alianças aparecem sempre. A cor de cada pesquisa é quem
              lidera no país.
            </span>
            <span className="flex items-center gap-3.5">
              {(["PROMISE", "CAMPAIGN", "ALLIANCE"] as const).map((kind) => (
                <span key={kind} className="flex items-center gap-1.5">
                  <MapMilestoneGlyph kind={kind} color={focus ? partyColor(focus) : "var(--faint-foreground)"} />
                  {MILESTONE_NAMES[kind]}
                </span>
              ))}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
