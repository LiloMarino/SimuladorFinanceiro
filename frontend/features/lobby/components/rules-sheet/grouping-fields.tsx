import type { CSSProperties } from "react";
import { Controller, type UseFormReturn } from "react-hook-form";
import { Info, Lock, Shield, Swords, Users, type LucideIcon } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import {
  Field,
  FieldContent,
  FieldDescription,
  FieldLabel,
  FieldLegend,
  FieldSet,
  FieldTitle,
} from "@/shared/components/ui/field";
import { RadioGroup, RadioGroupItem } from "@/shared/components/ui/radio-group";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { teamColor, teamShortName } from "@/shared/lib/teams";
import type { PlayerGrouping } from "@/types";
import type { SimulationFormValues } from "../../lib/simulation-form";

const GROUPING_OPTIONS: { value: PlayerGrouping; label: string; description: string; icon: LucideIcon }[] = [
  {
    value: "INDIVIDUAL",
    label: "Todos contra todos",
    description: "Cada um por si: vence a melhor carteira.",
    icon: Swords,
  },
  {
    value: "TEAMS",
    label: "Em equipes",
    description: "Cada um opera a própria carteira, mas vence a equipe com a melhor média.",
    icon: Users,
  },
];

type GroupingFieldsProps = {
  form: UseFormReturn<SimulationFormValues>;
  readOnly: boolean;
  grouping: SimulationFormValues["playerGrouping"];
  gameType: SimulationFormValues["gameType"];
};

/** Todos contra todos ou em equipes, com o nome das equipes. */
export function GroupingFields({ form, readOnly, grouping, gameType }: GroupingFieldsProps) {
  return (
    <FieldSet disabled={readOnly}>
      <FieldLegend variant="caption">Modo de jogo</FieldLegend>
      <Controller
        control={form.control}
        name="playerGrouping"
        render={({ field }) => (
          <RadioGroup
            value={field.value}
            onValueChange={(value) => field.onChange(value as PlayerGrouping)}
            disabled={readOnly}
            className="grid-cols-2"
          >
            {GROUPING_OPTIONS.map((option) => (
              <FieldLabel key={option.value} htmlFor={`grouping-${option.value}`}>
                <Field orientation="horizontal">
                  <RadioGroupItem
                    value={option.value}
                    id={`grouping-${option.value}`}
                    disabled={option.value === "TEAMS" && gameType === "POLITICAL"}
                  />
                  <FieldContent>
                    <FieldTitle>
                      <option.icon className="size-3.5 text-muted-foreground" />
                      {option.label}
                    </FieldTitle>
                    <FieldDescription>{option.description}</FieldDescription>
                  </FieldContent>
                </Field>
              </FieldLabel>
            ))}
          </RadioGroup>
        )}
      />
      {gameType === "POLITICAL" && (
        <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <Lock className="size-3.5" />
          Em equipes fica indisponível: na Política, os partidos já são os times.
        </div>
      )}
      {grouping === "TEAMS" && (
        <>
          <Controller
            control={form.control}
            name="teamNaming"
            render={({ field }) => (
              <div className="grid grid-cols-[1fr_auto] items-center gap-3 rounded-[10px] border p-3">
                <FieldContent>
                  <FieldTitle>Nome das equipes</FieldTitle>
                  <FieldDescription>Muda só o rótulo; a cor é a mesma.</FieldDescription>
                </FieldContent>
                <ToggleGroup
                  variant="segmented"
                  aria-label="Nome das equipes"
                  value={[field.value]}
                  onValueChange={(values) => values[0] && field.onChange(values[0])}
                  disabled={readOnly}
                >
                  {(["COLOR", "NUMBER"] as const).map((naming) => (
                    <ToggleGroupItem key={naming} value={naming} style={{ "--team": teamColor(2) } as CSSProperties}>
                      <Shield className="fill-(--team) stroke-(--team)" />
                      {teamShortName(2, naming)}
                    </ToggleGroupItem>
                  ))}
                </ToggleGroup>
              </div>
            )}
          />
          <Alert variant="info">
            <Info />
            <AlertTitle>Cada jogador escolhe a equipe no próprio card</AlertTitle>
            <AlertDescription>Começa todo mundo sem equipe. Equipes desiguais valem: conta a média.</AlertDescription>
          </Alert>
        </>
      )}
    </FieldSet>
  );
}
