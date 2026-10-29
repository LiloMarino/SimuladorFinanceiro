import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { displayDayMonth } from "@/shared/lib/utils/display";
import { useGuideBloc } from "../hooks/mutations/useGuideBloc";
import { causeLabel, orientationLabel, rangeLabel, type Vote } from "../lib/house";
import { VALUE_INFO } from "../lib/voters";

type Guide = NonNullable<Vote["guide"]>;

type GuideTileProps = {
  guide: Guide;
  /** A medida votada; nulo orienta o pedido de impeachment */
  measureId: number | null;
  /** Orientação que a bancada do líder tem hoje (a dele ou a padrão) */
  current: boolean;
  /** O que a votação decide, na frase da causa: "a medida" */
  subject: string;
};

/** "Você orienta o PRL": o líder escolhe Sim ou Não vendo o placar de cada cenário. */
export function GuideTile({ guide, measureId, current, subject }: GuideTileProps) {
  const orient = useGuideBloc();
  const pulled = guide.pulled_value ? VALUE_INFO[guide.pulled_value].label : null;

  return (
    <div className="grid gap-3 rounded-lg border border-info/30 bg-info-soft/30 p-3.5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="grid gap-0.5">
          <b className="text-sm">Você orienta o {guide.abbr}</b>
          <span className="text-xs text-muted-foreground">
            {guide.seats} cadeiras · muda até {displayDayMonth(guide.deadline)}, véspera da votação
          </span>
        </div>
        <ToggleGroup
          variant="segmented"
          aria-label={`Orientação do ${guide.abbr}`}
          value={[current ? "yes" : "no"]}
          disabled={orient.isPending}
          onValueChange={(values) => values[0] && orient.mutate({ measure_id: measureId, yes: values[0] === "yes" })}
        >
          <ToggleGroupItem value="yes">Sim</ToggleGroupItem>
          <ToggleGroupItem value="no">Não</ToggleGroupItem>
        </ToggleGroup>
      </div>

      <div className="grid gap-2.5 sm:grid-cols-2">
        {guide.scenarios.map((scenario) => {
          const why = causeLabel(
            {
              abbr: guide.abbr,
              cause: scenario.cause,
              cause_share: scenario.cause_share,
              orientation: scenario.orientation,
            },
            subject,
          );
          return (
            <div key={String(scenario.orientation)} className="rounded-md bg-card px-3 py-2 text-[13px] leading-normal">
              <b>Se {scenario.orientation ? "orientar Sim" : "ficar Não"}</b>
              <br />
              Sim {rangeLabel(scenario.low, scenario.high)}.{" "}
              {scenario.may_defect === 0
                ? `Ninguém do ${guide.abbr} desobedece.`
                : `Até ${scenario.may_defect} do ${guide.abbr} votariam ${orientationLabel(!scenario.orientation)}${why ? `: ${why}` : ""}.`}
            </div>
          );
        })}
      </div>

      <span className="text-xs text-muted-foreground">
        Sem orientação, o {guide.abbr} vota {orientationLabel(guide.default_orientation)}
        {pulled ? `, porque a votação puxa para ${pulled}` : ""}.
        {guide.yes_moves.length > 0 && " Orientar Sim também move o perfil do partido."}
      </span>
    </div>
  );
}
