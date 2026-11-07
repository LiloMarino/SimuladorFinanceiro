import { Controller, type UseFormReturn } from "react-hook-form";
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
import { VICTORY_CRITERIA } from "@/shared/lib/victory-criteria";
import type { VictoryCriterion } from "@/types";
import type { SimulationFormValues } from "../../lib/simulation-form";

type VictoryFieldsProps = {
  form: UseFormReturn<SimulationFormValues>;
  readOnly: boolean;
  grouping: SimulationFormValues["playerGrouping"];
};

/** O critério de vitória da partida clássica. */
export function VictoryFields({ form, readOnly, grouping }: VictoryFieldsProps) {
  return (
    <FieldSet disabled={readOnly}>
      <FieldLegend variant="caption">
        Quem vence{grouping === "TEAMS" ? " (em equipes: a média dos membros)" : ""}
      </FieldLegend>
      <Controller
        control={form.control}
        name="victoryCriterion"
        render={({ field }) => (
          <RadioGroup
            value={field.value}
            onValueChange={(value) => field.onChange(value as VictoryCriterion)}
            disabled={readOnly}
            className="grid-cols-2"
          >
            {Object.entries(VICTORY_CRITERIA).map(([value, criterion]) => (
              <FieldLabel key={value} htmlFor={`criterion-${value}`}>
                <Field orientation="horizontal">
                  <RadioGroupItem value={value} id={`criterion-${value}`} />
                  <FieldContent>
                    <FieldTitle>{criterion.label}</FieldTitle>
                    <FieldDescription>{criterion.description}</FieldDescription>
                  </FieldContent>
                </Field>
              </FieldLabel>
            ))}
          </RadioGroup>
        )}
      />
    </FieldSet>
  );
}
