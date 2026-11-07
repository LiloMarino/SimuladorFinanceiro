import { Controller, type UseFormReturn } from "react-hook-form";
import { Field, FieldError, FieldLabel, FieldLegend, FieldSet } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { PRICE_IMPACT_MODE_LABELS, type PriceImpactMode } from "@/shared/lib/price-impact";
import { formatPositiveInteger } from "@/shared/lib/utils/format";
import type { SimulationFormValues } from "../../lib/simulation-form";
import { PriceImpactExample } from "../price-impact-example";

type PriceImpactFieldsProps = {
  form: UseFormReturn<SimulationFormValues>;
  readOnly: boolean;
  mode: PriceImpactMode;
  enabled: SimulationFormValues["priceImpactEnabled"];
  k: SimulationFormValues["priceImpactK"];
  decayDays: SimulationFormValues["priceImpactDecayDays"];
  /** Ativo citado no exemplo do impacto; vazio quando a base não tem ação */
  exampleTicker: string | undefined;
  onSelectMode: (mode: PriceImpactMode) => void;
};

/** O modo do impacto de preço das ordens e, no personalizado, os dois parâmetros. */
export function PriceImpactFields({
  form,
  readOnly,
  mode,
  enabled,
  k,
  decayDays,
  exampleTicker,
  onSelectMode,
}: PriceImpactFieldsProps) {
  return (
    <FieldSet disabled={readOnly}>
      <FieldLegend variant="caption">Mercado · impacto de preço das ordens</FieldLegend>
      <ToggleGroup
        variant="segmented"
        aria-label="Impacto de preço"
        value={[mode]}
        onValueChange={(values) => values[0] && onSelectMode(values[0] as PriceImpactMode)}
        disabled={readOnly}
        className="w-full"
      >
        {(Object.keys(PRICE_IMPACT_MODE_LABELS) as PriceImpactMode[]).map((option) => (
          <ToggleGroupItem key={option} value={option} className="flex-1">
            {PRICE_IMPACT_MODE_LABELS[option]}
          </ToggleGroupItem>
        ))}
      </ToggleGroup>

      {mode === "CUSTOM" && (
        <div className="grid grid-cols-2 gap-3">
          <Controller
            control={form.control}
            name="priceImpactK"
            render={({ field, fieldState }) => (
              <Field data-invalid={fieldState.invalid}>
                <FieldLabel htmlFor="rules-k">Intensidade (k)</FieldLabel>
                <Input {...field} id="rules-k" inputMode="decimal" numeric aria-invalid={fieldState.invalid} />
                <FieldError errors={[fieldState.error]} />
              </Field>
            )}
          />
          <Controller
            control={form.control}
            name="priceImpactDecayDays"
            render={({ field, fieldState }) => (
              <Field data-invalid={fieldState.invalid}>
                <FieldLabel htmlFor="rules-t">Volta ao histórico (T, em pregões)</FieldLabel>
                <Input
                  {...field}
                  id="rules-t"
                  inputMode="numeric"
                  numeric
                  aria-invalid={fieldState.invalid}
                  onChange={(e) => field.onChange(formatPositiveInteger(e.target.value))}
                />
                <FieldError errors={[fieldState.error]} />
              </Field>
            )}
          />
        </div>
      )}

      {enabled && <PriceImpactExample k={k} decayDays={decayDays} ticker={exampleTicker} />}
    </FieldSet>
  );
}
