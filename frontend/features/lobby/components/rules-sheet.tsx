import { useEffect, useState } from "react";
import { Controller, useWatch, type UseFormReturn } from "react-hook-form";
import { CircleCheck, TriangleAlert } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import {
  Field,
  FieldContent,
  FieldDescription,
  FieldError,
  FieldLabel,
  FieldLegend,
  FieldSet,
  FieldTitle,
} from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { RadioGroup, RadioGroupItem } from "@/shared/components/ui/radio-group";
import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from "@/shared/components/ui/sheet";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import type ApiError from "@/shared/lib/models/ApiError";
import { formatMoney, formatPositiveInteger } from "@/shared/lib/utils/format";
import { displayDecimal } from "@/shared/lib/utils/display";
import { VICTORY_CRITERIA } from "@/shared/lib/victory-criteria";
import type { VictoryCriterion } from "@/types";
import type { CoverageCheck } from "../lib/coverage";
import {
  PRICE_IMPACT_MODE_LABELS,
  PRICE_IMPACT_PRESETS,
  priceImpactModeOf,
  type PriceImpactMode,
} from "../lib/price-impact";
import { CoverageAlerts } from "./coverage-alerts";
import { DateField } from "./date-field";
import type { SimulationFormValues } from "./lobby-match";
import { PriceImpactExample } from "./price-impact-example";

type RulesSheetProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  form: UseFormReturn<SimulationFormValues>;
  isHost: boolean;
  hostNickname: string;
  coverageCheck: CoverageCheck;
  /** Ativo citado no exemplo do impacto; vazio quando a base não tem ação */
  exampleTicker: string | undefined;
  saveStatus: { savedAt: number | null; saving: boolean; saveError: ApiError | null };
  /** Regras gravadas numa partida salva: valem como estão, ninguém edita */
  locked?: boolean;
};

/** Regras da partida num painel lateral, com o lobby atrás. Mudanças salvam sozinhas. */
export function RulesSheet({
  open,
  onOpenChange,
  form,
  isHost,
  hostNickname,
  coverageCheck,
  exampleTicker,
  saveStatus,
  locked = false,
}: RulesSheetProps) {
  const [startDate, impactEnabled, impactK, impactT] = useWatch({
    control: form.control,
    name: ["startDate", "priceImpactEnabled", "priceImpactK", "priceImpactDecayDays"],
  });
  // Personalizado fica aberto mesmo quando k e T coincidem com um preset
  const [customOpen, setCustomOpen] = useState(false);
  const derivedMode = priceImpactModeOf(impactEnabled, impactK, impactT);
  const impactMode: PriceImpactMode = customOpen && impactEnabled ? "CUSTOM" : derivedMode;
  const readOnly = !isHost || locked;

  const selectImpactMode = (mode: PriceImpactMode) => {
    setCustomOpen(mode === "CUSTOM");
    form.setValue("priceImpactEnabled", mode !== "OFF", { shouldValidate: true });
    if (mode === "REALISTIC" || mode === "STRONG") {
      const preset = PRICE_IMPACT_PRESETS[mode];
      form.setValue("priceImpactK", displayDecimal(preset.k), { shouldValidate: true });
      form.setValue("priceImpactDecayDays", String(preset.decayDays), { shouldValidate: true });
    }
  };

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent size="lg">
        <SheetHeader>
          <SheetTitle>Regras da partida</SheetTitle>
          <SheetDescription>
            {locked
              ? "São as regras gravadas na partida salva: não mudam."
              : isHost
                ? "Mudanças salvam sozinhas e aparecem pra todos."
                : "Modo visualização."}
          </SheetDescription>
        </SheetHeader>

        <form className="flex flex-1 flex-col gap-7 overflow-y-auto px-6 py-5" onSubmit={(e) => e.preventDefault()}>
          {/* Básico */}
          <FieldSet disabled={readOnly}>
            <FieldLegend variant="caption">Básico</FieldLegend>
            <Controller
              control={form.control}
              name="name"
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="rules-name">Nome</FieldLabel>
                  <Input {...field} id="rules-name" aria-invalid={fieldState.invalid} />
                  <FieldError errors={[fieldState.error]} />
                </Field>
              )}
            />
            <div className="grid grid-cols-2 gap-3">
              {(["startDate", "endDate"] as const).map((name) => (
                <Controller
                  key={name}
                  control={form.control}
                  name={name}
                  render={({ field, fieldState }) => (
                    <Field data-invalid={fieldState.invalid}>
                      <FieldLabel htmlFor={`rules-${name}`}>{name === "startDate" ? "Início" : "Fim"}</FieldLabel>
                      <DateField
                        id={`rules-${name}`}
                        value={field.value}
                        onChange={field.onChange}
                        onBlur={field.onBlur}
                        invalid={fieldState.invalid}
                      />
                      <FieldError errors={[fieldState.error]} />
                    </Field>
                  )}
                />
              ))}
            </div>
            <CoverageAlerts check={coverageCheck} startDate={startDate} />
            <div className="grid grid-cols-2 gap-3">
              {(
                [
                  ["startingCash", "Saldo inicial"],
                  ["monthlyContribution", "Aporte mensal"],
                ] as const
              ).map(([name, label]) => (
                <Controller
                  key={name}
                  control={form.control}
                  name={name}
                  render={({ field, fieldState }) => (
                    <Field data-invalid={fieldState.invalid}>
                      <FieldLabel htmlFor={`rules-${name}`}>{label}</FieldLabel>
                      <Input
                        {...field}
                        id={`rules-${name}`}
                        inputMode="decimal"
                        numeric
                        aria-invalid={fieldState.invalid}
                        onChange={(e) => field.onChange(formatMoney(e.target.value))}
                      />
                      <FieldError errors={[fieldState.error]} />
                    </Field>
                  )}
                />
              ))}
            </div>
          </FieldSet>

          {/* Quem vence */}
          <FieldSet disabled={readOnly}>
            <FieldLegend variant="caption">Quem vence</FieldLegend>
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

          {/* Impacto de preço */}
          <FieldSet disabled={readOnly}>
            <FieldLegend variant="caption">Mercado · impacto de preço das ordens</FieldLegend>
            <ToggleGroup
              variant="segmented"
              aria-label="Impacto de preço"
              value={[impactMode]}
              onValueChange={(values) => values[0] && selectImpactMode(values[0] as PriceImpactMode)}
              disabled={readOnly}
              className="w-full"
            >
              {(Object.keys(PRICE_IMPACT_MODE_LABELS) as PriceImpactMode[]).map((mode) => (
                <ToggleGroupItem key={mode} value={mode} className="flex-1">
                  {PRICE_IMPACT_MODE_LABELS[mode]}
                </ToggleGroupItem>
              ))}
            </ToggleGroup>

            {impactMode === "CUSTOM" && (
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

            {impactEnabled && <PriceImpactExample k={impactK} decayDays={impactT} ticker={exampleTicker} />}
          </FieldSet>
        </form>

        <SheetFooter>
          <SaveStatus
            isHost={isHost}
            locked={locked}
            hostNickname={hostNickname}
            invalidFields={Object.keys(form.formState.errors).length}
            {...saveStatus}
          />
          <SheetClose render={<Button variant="outline" />}>Fechar</SheetClose>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  );
}

type SaveStatusProps = RulesSheetProps["saveStatus"] & {
  isHost: boolean;
  locked: boolean;
  hostNickname: string;
  invalidFields: number;
};

/** Rodapé do painel: o que aconteceu com a última mudança, no lugar do toast repetido. */
function SaveStatus({ isHost, locked, hostNickname, invalidFields, savedAt, saving, saveError }: SaveStatusProps) {
  const now = useNow(1000);

  if (locked) {
    return <span className="text-[13px] text-muted-foreground">Regras de uma partida salva não mudam.</span>;
  }

  if (!isHost) {
    return (
      <span className="text-[13px] text-muted-foreground">
        Só {hostNickname} (host) edita. Você vê as mudanças na hora.
      </span>
    );
  }
  if (invalidFields > 0 || saveError) {
    return (
      <span className="flex items-center gap-1.5 text-[13px] text-destructive">
        <TriangleAlert className="size-3.5" />
        {invalidFields > 0
          ? `${invalidFields} ${invalidFields === 1 ? "campo com problema" : "campos com problema"}: nada foi salvo`
          : `Não salvou: ${saveError?.message}`}
      </span>
    );
  }
  if (saving) return <span className="text-[13px] text-muted-foreground">Salvando…</span>;
  if (savedAt) {
    const seconds = Math.max(0, Math.round((now - savedAt) / 1000));
    return (
      <span className="flex items-center gap-1.5 text-xs text-success">
        <CircleCheck className="size-3.5" />
        Salvo há {seconds} s · todos já veem
      </span>
    );
  }
  return <span className="text-[13px] text-muted-foreground">Mudanças salvam sozinhas.</span>;
}

/** Relógio que avança a cada `intervalMs`, para textos como "há 3 s". */
function useNow(intervalMs: number) {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const timer = setInterval(() => setNow(Date.now()), intervalMs);
    return () => clearInterval(timer);
  }, [intervalMs]);
  return now;
}
