import { Controller, type UseFormReturn } from "react-hook-form";
import { Info, Lock } from "lucide-react";
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
import { EXPANSIONS, type ExpansionKey } from "@/shared/lib/expansions";
import { BASE_GAME_TYPE_OPTIONS, EXPANSION_GAME_TYPE_OPTIONS } from "@/shared/lib/game-types";
import type { GameType } from "@/types";
import type { SimulationFormValues } from "../../lib/simulation-form";

type GameTypeFieldsProps = {
  form: UseFormReturn<SimulationFormValues>;
  readOnly: boolean;
  /** Quais expansões estão ligadas: os tipos de expansão só se escolhem com a delas ligada */
  expansions: Record<ExpansionKey, boolean>;
  grouping: SimulationFormValues["playerGrouping"];
  /** Troca o tipo: recebe o `onChange` do campo, que registra a escolha no formulário */
  onSelect: (value: GameType, onChange: (value: GameType) => void) => void;
};

/** Os tipos de partida, com os que as expansões acrescentam. */
export function GameTypeFields({ form, readOnly, expansions, grouping, onSelect }: GameTypeFieldsProps) {
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

            {/* Tipos que a expansão acrescenta */}
            <div className="grid gap-2">
              <span className="text-xs text-muted-foreground">Das expansões</span>
              <RadioGroup
                value={field.value}
                onValueChange={(value) => onSelect(value as GameType, field.onChange)}
                disabled={readOnly}
              >
                {EXPANSION_GAME_TYPE_OPTIONS.map(([value, type]) => {
                  const expansion = EXPANSIONS[type.expansion];
                  const expansionOn = expansions[type.expansion];
                  const teamsBlock = grouping === "TEAMS";
                  return (
                    <FieldLabel key={value} htmlFor={`game-type-${value}`}>
                      <Field>
                        <div className="flex items-center justify-between">
                          <type.icon className="size-[18px] text-muted-foreground" />
                          <RadioGroupItem
                            value={value}
                            id={`game-type-${value}`}
                            variant={type.expansion === "funds" ? "fund" : "default"}
                            disabled={!expansionOn || teamsBlock}
                          />
                        </div>
                        <FieldContent>
                          <FieldTitle>{type.label}</FieldTitle>
                          <FieldDescription>{type.description}</FieldDescription>
                          {!expansionOn && (
                            <Badge variant="secondary" className="w-fit">
                              <Lock className="size-3.5" />
                              Ligue a expansão {expansion.label}
                            </Badge>
                          )}
                          {expansionOn && field.value === value && (
                            <Badge variant={type.expansion === "funds" ? "fund" : "government"} className="w-fit">
                              <ExpansionEmblem expansion={type.expansion} size="xs" />
                              expansão {expansion.label} ligada e travada
                            </Badge>
                          )}
                          {expansionOn && teamsBlock && (
                            <Badge variant="secondary" size="sm" className="w-fit">
                              Só em Todos contra todos
                            </Badge>
                          )}
                        </FieldContent>
                      </Field>
                    </FieldLabel>
                  );
                })}
              </RadioGroup>
              {grouping === "TEAMS" && (
                <Alert variant="muted">
                  <Info />
                  <AlertDescription>
                    Em equipes o time já está definido. Para disputar por partidos ou por aquisição hostil, volte a
                    Todos contra todos.
                  </AlertDescription>
                </Alert>
              )}
            </div>
          </>
        )}
      />
    </FieldSet>
  );
}
