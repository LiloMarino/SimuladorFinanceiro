import { useState } from "react";
import { Handshake } from "lucide-react";
import { Alert, AlertAction, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { displayDayMonth } from "@/shared/lib/utils/display";
import { useGuideBloc } from "../hooks/mutations/useGuideBloc";
import { useBase } from "../hooks/queries/useBase";
import { groupsLabel } from "../lib/base";
import { causeLabel, orientationLabel, rangeLabel, type Vote } from "../lib/house";
import { VALUE_INFO } from "@/shared/lib/party-flags";

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
  const [confirming, setConfirming] = useState(false);
  const { data: base } = useBase({ enabled: guide.by_deal });
  const governmentGroups = base?.my_deal?.government_groups ?? [];
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
          onValueChange={(values) => {
            const yes = values[0] === "yes";
            if (!values[0]) return;
            // Com acordo em vigor, orientar Não rompe o acordo e pede confirmação
            if (guide.by_deal && !yes) setConfirming(true);
            else orient.mutate({ measure_id: measureId, yes, break_deal: false });
          }}
        >
          <ToggleGroupItem value="yes">Sim</ToggleGroupItem>
          <ToggleGroupItem value="no">Não</ToggleGroupItem>
        </ToggleGroup>
      </div>

      {guide.by_deal && (
        <Alert variant={confirming ? "warning" : "info"}>
          <Handshake />
          <AlertTitle>
            {confirming ? "Orientar Não rompe o acordo com o governo" : "A orientação Sim vem do acordo com o governo"}
          </AlertTitle>
          <AlertDescription>
            {confirming
              ? `A emenda para${governmentGroups.length > 0 ? `, e ${groupsLabel(governmentGroups).toLowerCase()} somam +8 de rejeição ao ${guide.abbr}` : ` e o ${guide.abbr} soma +8 de rejeição`}.`
              : `Enquanto o acordo valer, o ${guide.abbr} orienta Sim em tudo o que o governo propõe.`}
          </AlertDescription>
          {confirming && (
            <AlertAction>
              <span className="flex gap-2">
                <Button size="xs" variant="outline" onClick={() => setConfirming(false)}>
                  Voltar para Sim
                </Button>
                <Button
                  size="xs"
                  variant="destructive"
                  disabled={orient.isPending}
                  onClick={() =>
                    orient.mutate(
                      { measure_id: measureId, yes: false, break_deal: true },
                      { onSuccess: () => setConfirming(false) },
                    )
                  }
                >
                  Orientar Não e romper
                </Button>
              </span>
            </AlertAction>
          )}
        </Alert>
      )}

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
