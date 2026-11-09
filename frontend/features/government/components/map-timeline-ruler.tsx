import type { ReactNode } from "react";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/shared/components/ui/tooltip";
import { useElementWidth } from "@/shared/hooks/useElementWidth";
import { cn } from "@/shared/lib/utils";
import { partyColor } from "@/shared/lib/party-colors";
import type { ElectionTimeline, MapParty, MapPlace, TimelineMilestone, TimelinePoint } from "@/types";
import { milestoneTip, type MilestoneContext, type MilestoneTip } from "../lib/map-milestones";
import {
  finalists,
  fullDate,
  milestoneCount,
  milestoneSlots,
  pointLabel,
  RULER_MARGIN,
  rulerLayout,
  type MilestoneSlot,
} from "../lib/map-timeline";
import { MapMilestoneGlyph } from "./map-milestone-glyph";

const AXIS_TOP = 45;
const NEUTRAL_COLOR = "var(--faint-foreground)";
/** O ponto a menos que isto da borda direita leva a bandeira alinhada à direita. */
const FLAG_EDGE = 70;

type MapTimelineRulerProps = {
  timeline: ElectionTimeline;
  selected: TimelinePoint;
  /** O texto da bandeira sobre o ponto escolhido. */
  flag: string;
  /** O partido em foco: dono das promessas e ações que aparecem na faixa de marcos. */
  focusParty: number | null;
  regions: MapPlace[];
  onSelect: (point: TimelinePoint) => void;
};

function partyById(parties: MapParty[], id: number | undefined) {
  const party = parties.find((item) => item.id === id);
  return party ? partyColor(party) : NEUTRAL_COLOR;
}

// O 1º turno leva as duas cores dos finalistas; os demais pontos, a cor de quem lidera no país
function pointFill(point: TimelinePoint, parties: MapParty[], runoffPair: number[]) {
  if (point.kind === "FIRST_ROUND" && runoffPair.length === 2) {
    return `linear-gradient(135deg, ${partyById(parties, runoffPair[0])} 50%, ${partyById(parties, runoffPair[1])} 50%)`;
  }
  return partyById(parties, point.leaders[0]);
}

function TipBody({ tip }: { tip: MilestoneTip }) {
  return (
    <div className="grid gap-1">
      <span className="font-semibold">{tip.title}</span>
      <span className="opacity-70">{tip.span}</span>
      {tip.lines.map((line) => (
        <span key={line}>• {line}</span>
      ))}
      {tip.effect && <span className="mt-0.5 border-t border-background/20 pt-1.5">{tip.effect}</span>}
    </div>
  );
}

type MilestoneChipProps = {
  label: string;
  tip: ReactNode;
  children: ReactNode;
};

function MilestoneChip({ label, tip, children }: MilestoneChipProps) {
  return (
    <Tooltip>
      <TooltipTrigger render={<button type="button" aria-label={label} />}>{children}</TooltipTrigger>
      <TooltipContent side="top" className="max-w-80 items-start">
        {tip}
      </TooltipContent>
    </Tooltip>
  );
}

type SlotMarkersProps = {
  slot: MilestoneSlot;
  x: number;
  parties: MapParty[];
  context: MilestoneContext;
};

function SlotMarkers({ slot, x, parties, context }: SlotMarkersProps) {
  const tipOf = (milestone: TimelineMilestone) => milestoneTip(milestone, context);
  return (
    <div className="absolute top-[88px] flex -translate-x-1/2 gap-[3px]" style={{ left: x }}>
      {slot.shown.map((milestone, index) => {
        const tip = tipOf(milestone);
        return (
          <MilestoneChip
            key={`${milestone.kind}-${milestone.party_id}-${index}`}
            label={tip.title}
            tip={<TipBody tip={tip} />}
          >
            <MapMilestoneGlyph
              kind={milestone.kind}
              color={partyById(parties, milestone.party_id)}
              count={milestoneCount(milestone)}
            />
          </MilestoneChip>
        );
      })}
      {slot.hidden.length > 0 && (
        <MilestoneChip
          label={`Mais ${slot.hidden.length} marcos`}
          tip={
            <div className="grid gap-2">
              {slot.all.map((milestone, index) => (
                <TipBody key={index} tip={tipOf(milestone)} />
              ))}
            </div>
          }
        >
          <span className="inline-flex h-6 items-center rounded-md border bg-card px-1.5 text-xs font-bold text-muted-foreground">
            +{slot.hidden.length}
          </span>
        </MilestoneChip>
      )}
    </div>
  );
}

function Bracket({ from, to, label }: { from: number; to: number; label: string }) {
  return (
    <>
      <span
        className="absolute top-0 text-xs font-semibold tracking-wide whitespace-nowrap text-faint-foreground uppercase"
        style={{ left: from }}
      >
        {label}
      </span>
      <span
        className="absolute top-4 h-1.5 rounded-t border-x-[1.5px] border-t-[1.5px] border-input"
        style={{ left: from, width: to - from }}
      />
    </>
  );
}

/** A régua do ano: um ponto por pesquisa, losangos nos turnos e a faixa de marcos embaixo. */
export function MapTimelineRuler({ timeline, selected, flag, focusParty, regions, onSelect }: MapTimelineRulerProps) {
  const [attach, width] = useElementWidth<HTMLDivElement>();
  const { points, parties } = timeline;
  const { xs } = rulerLayout(points, width);
  const runoffPair = finalists(points);
  const context: MilestoneContext = { parties, points, regions };
  const firstX = xs[0] ?? RULER_MARGIN;
  const lastX = xs.at(-1) ?? RULER_MARGIN;

  const firstRoundIndex = points.findIndex((point) => point.kind === "FIRST_ROUND");
  const runoffStartIndex = points.findIndex((point) => point.kind === "RUNOFF_POLL" || point.kind === "RUNOFF");
  const selectedIndex = points.findIndex((point) => point.date === selected.date);
  const selectedX = xs[selectedIndex] ?? firstX;

  return (
    <div ref={attach} className="relative mt-5.5 h-[122px]">
      {width > 0 && (
        <>
          {/* Colchetes dos dois turnos */}
          {firstRoundIndex > 0 && (
            <Bracket from={firstX} to={xs[firstRoundIndex]!} label="1º turno · uma pesquisa por mês" />
          )}
          {runoffStartIndex > 0 && (
            <Bracket from={xs[runoffStartIndex]!} to={lastX} label="2º turno · uma por semana" />
          )}

          {/* Eixo */}
          {points.slice(1).map((point, index) => {
            const before = points[index]!;
            const gapWithoutPolls = before.kind === "POLL" && point.kind === "FIRST_ROUND";
            return (
              <span
                key={point.date}
                className={cn(
                  "absolute h-0.5 rounded-full bg-faint-foreground/45",
                  !point.happened && "border-t-2 border-dashed border-faint-foreground/45 bg-transparent",
                  gapWithoutPolls && "opacity-50",
                )}
                style={{ left: xs[index], width: xs[index + 1]! - xs[index]!, top: AXIS_TOP }}
              />
            );
          })}

          {/* Anel do ponto escolhido e bandeira com a data */}
          <span
            className="absolute size-6.5 -translate-x-1/2 -translate-y-1/2 rounded-full ring-3 ring-primary"
            style={{ left: selectedX, top: AXIS_TOP + 1 }}
            aria-hidden
          />
          <span
            className={cn(
              "absolute -top-6 rounded-md bg-primary px-2 py-0.5 text-xs font-semibold whitespace-nowrap text-primary-foreground",
              width - selectedX < FLAG_EDGE ? "-translate-x-[calc(100%-18px)]" : "-translate-x-1/2",
            )}
            style={{ left: selectedX }}
          >
            {flag}
          </span>

          {/* Pontos e rótulos */}
          {points.map((point, index) => {
            const isTurn = point.kind === "FIRST_ROUND" || point.kind === "RUNOFF";
            const isSelected = point.date === selected.date;
            const name = isTurn ? pointLabel(point) : "Pesquisa";
            return (
              <div key={point.date}>
                <button
                  type="button"
                  disabled={!point.happened}
                  aria-label={`${name} de ${fullDate(point.date)}`}
                  aria-current={isSelected ? "true" : undefined}
                  onClick={() => onSelect(point)}
                  className="absolute grid size-7 -translate-x-1/2 -translate-y-1/2 place-items-center rounded-full outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-default"
                  style={{ left: xs[index], top: AXIS_TOP + 1 }}
                >
                  <span
                    className={cn(
                      "block ring-2 ring-card",
                      isTurn ? "size-3.75 rotate-45 rounded-[3px]" : "size-3 rounded-full",
                      !point.happened && "border-[1.5px] border-dashed border-faint-foreground bg-card ring-0",
                    )}
                    style={point.happened ? { background: pointFill(point, parties, runoffPair) } : undefined}
                  />
                </button>
                <span
                  className={cn(
                    "absolute top-[62px] -translate-x-1/2 font-mono text-xs whitespace-nowrap text-faint-foreground",
                    (isSelected || isTurn) && "font-semibold text-foreground",
                  )}
                  style={{ left: xs[index] }}
                >
                  {pointLabel(point)}
                </span>
              </div>
            );
          })}

          {/* Faixa de marcos */}
          <span className="absolute top-[100px] h-px bg-border" style={{ left: firstX, width: lastX - firstX }} />
          {milestoneSlots(timeline.milestones, focusParty).map((slot) => {
            const from = points.findIndex((point) => point.date === slot.after);
            const to = points.findIndex((point) => point.date === slot.before);
            if (from === -1 || to === -1) return null;
            return (
              <SlotMarkers
                key={slot.after}
                slot={slot}
                x={(xs[from]! + xs[to]!) / 2}
                parties={parties}
                context={context}
              />
            );
          })}
        </>
      )}
    </div>
  );
}
