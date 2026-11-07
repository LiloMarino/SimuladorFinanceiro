import { Controller, type UseFormReturn } from "react-hook-form";
import { Info } from "lucide-react";
import { ExpansionEmblem } from "@/shared/components/expansion-emblem";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
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
import { EXPANSIONS } from "@/shared/lib/expansions";
import { BASE_GAME_TYPE_OPTIONS, POLITICAL_GAME_TYPE } from "@/shared/lib/game-types";
import type { GameType } from "@/types";
import type { SimulationFormValues } from "../../lib/simulation-form";

type GameTypeFieldsProps = {
  form: UseFormReturn<SimulationFormValues>;
  readOnly: boolean;
  governmentEnabled: SimulationFormValues["governmentEnabled"];
  grouping: SimulationFormValues["playerGrouping"];
  /** Troca o tipo: recebe o `onChange` do campo, que registra a escolha no formulário */
  onSelect: (value: GameType, onChange: (value: GameType) => void) => void;
};

/** Os tipos de partida, com o que a expansão do governo acrescenta. */
export function GameTypeFields({ form, readOnly, governmentEnabled, grouping, onSelect }: GameTypeFieldsProps) {
  return (
    <FieldSet disabled={readOnly}>
      <FieldLegend variant="caption">Tipo de partida</FieldLegend>
      <Controller
        control={form.control}
        name="gameType"
        render={({ field }) => (
          <>
            <RadioGroup
              value={field.value}
              onValueChange={(value) => onSelect(value as GameType, field.onChange)}
              disabled={readOnly}
              className="grid-flow-col auto-cols-fr"
            >
              {BASE_GAME_TYPE_OPTIONS.map(([value, type]) => (
                <FieldLabel key={value} htmlFor={`game-type-${value}`}>
                  <Field>
                    <div className="flex items-center justify-between">
                      <type.icon className="size-[18px] text-muted-foreground" />
                      <RadioGroupItem value={value} id={`game-type-${value}`} />
                    </div>
                    <FieldContent>
                      <FieldTitle>{type.label}</FieldTitle>
                      <FieldDescription>{type.description}</FieldDescription>
                    </FieldContent>
                  </Field>
                </FieldLabel>
              ))}
            </RadioGroup>

            {/* Tipo que a expansão acrescenta */}
            {governmentEnabled ? (
              <div className="grid gap-2">
                <span className="text-xs text-muted-foreground">Expansão ligada nesta partida</span>
                <RadioGroup
                  value={field.value}
                  onValueChange={(value) => onSelect(value as GameType, field.onChange)}
                  disabled={readOnly}
                >
                  <FieldLabel htmlFor="game-type-POLITICAL">
                    <Field>
                      <div className="flex items-center justify-between">
                        <POLITICAL_GAME_TYPE.icon className="size-[18px] text-primary" />
                        <RadioGroupItem value="POLITICAL" id="game-type-POLITICAL" disabled={grouping === "TEAMS"} />
                      </div>
                      <FieldContent>
                        <FieldTitle>
                          {POLITICAL_GAME_TYPE.label}
                          <Badge variant="outline" size="sm">
                            <ExpansionEmblem expansion="government" size="xs" />
                            {EXPANSIONS.government.label}
                          </Badge>
                          {grouping === "TEAMS" && (
                            <Badge variant="secondary" size="sm">
                              Só em Todos contra todos
                            </Badge>
                          )}
                        </FieldTitle>
                        <FieldDescription>{POLITICAL_GAME_TYPE.description}</FieldDescription>
                      </FieldContent>
                    </Field>
                  </FieldLabel>
                </RadioGroup>
                {grouping === "TEAMS" && (
                  <Alert variant="muted">
                    <Info />
                    <AlertDescription>
                      Em equipes o time já está definido. Para disputar por partidos, volte a Todos contra todos.
                    </AlertDescription>
                  </Alert>
                )}
              </div>
            ) : (
              <Alert variant="muted">
                <Info />
                <AlertDescription>
                  A expansão {EXPANSIONS.government.label} acrescenta o tipo “{POLITICAL_GAME_TYPE.label}”. Ligue na aba
                  Expansões.
                </AlertDescription>
              </Alert>
            )}
          </>
        )}
      />
    </FieldSet>
  );
}
