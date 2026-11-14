import { Controller, useWatch, type UseFormReturn } from "react-hook-form";
import { Field, FieldDescription, FieldError, FieldLabel } from "@/shared/components/ui/field";
import { InfoHint } from "@/shared/components/info-hint";
import { InputGroup, InputGroupAddon, InputGroupInput, InputGroupText } from "@/shared/components/ui/input-group";
import { Switch } from "@/shared/components/ui/switch";
import { EXPANSIONS } from "@/shared/lib/expansions";
import { displayDecimal, displayMoneyWhole } from "@/shared/lib/utils/display";
import { cn } from "@/shared/lib/utils";
import { managementFeeExample, performanceFeeExample } from "../lib/fund-rules";
import type { SimulationFormValues } from "../lib/simulation-form";
import { ExpansionIntro } from "./expansion-intro";

const FUNDS = EXPANSIONS.funds;

type FundsCardProps = {
  form: UseFormReturn<SimulationFormValues>;
  /** Sem edição: convidado ou regras de uma partida salva */
  readOnly: boolean;
};

/** O cartão "Gestoras": a chave da expansão e os tetos das taxas que cada gestor pode cobrar. */
export function FundsCard({ form, readOnly }: FundsCardProps) {
  const [enabled, managementCap, performanceCap] = useWatch({
    control: form.control,
    name: ["fundsEnabled", "fundMaxManagementFee", "fundMaxPerformanceFee"],
  });
  const monthlyFee = managementFeeExample(managementCap);
  const performance = performanceFeeExample(performanceCap);

  return (
    <div className={cn("self-start overflow-hidden rounded-xl border bg-card", enabled && "border-2 border-primary")}>
      <ExpansionIntro expansion="funds" enabled={enabled}>
        <Controller
          control={form.control}
          name="fundsEnabled"
          render={({ field }) => (
            <Switch
              aria-label={`Ligar ${FUNDS.label}`}
              checked={field.value}
              disabled={readOnly}
              onCheckedChange={field.onChange}
            />
          )}
        />
      </ExpansionIntro>

      {/* Tetos de taxa */}
      {enabled && (
        <div className="grid gap-3.5 border-t px-4 py-3.5">
          <Controller
            control={form.control}
            name="fundMaxManagementFee"
            render={({ field, fieldState }) => (
              <Field data-invalid={fieldState.invalid}>
                <FieldLabel htmlFor="rules-fundMaxManagementFee">
                  Taxa de administração máx.
                  <InfoHint label="O que é a taxa de administração">
                    <div className="space-y-1 text-left">
                      <p>
                        É o que o gestor cobra por ano sobre o patrimônio da gestora, descontado todo mês, em 12
                        parcelas.
                      </p>
                      <p>
                        Ex.: com 2% ao ano e R$ 1 milhão de patrimônio, o gestor recebe R$ 1.667 por mês (1.000.000 × 2%
                        ÷ 12).
                      </p>
                    </div>
                  </InfoHint>
                </FieldLabel>
                <InputGroup>
                  <InputGroupInput
                    {...field}
                    id="rules-fundMaxManagementFee"
                    inputMode="decimal"
                    numeric
                    disabled={readOnly}
                    aria-invalid={fieldState.invalid}
                    onChange={(e) => field.onChange(e.target.value.replace(/[^\d,]/g, ""))}
                  />
                  <InputGroupAddon align="inline-end">
                    <InputGroupText>% ao ano</InputGroupText>
                  </InputGroupAddon>
                </InputGroup>
                <FieldDescription>
                  {monthlyFee === null
                    ? "Sobre o patrimônio da gestora, todo mês."
                    : `Sobre o patrimônio da gestora, todo mês. Com ${managementCap}% e R$ 1 milhão, o gestor recebe ${displayMoneyWhole(monthlyFee)} por mês.`}
                </FieldDescription>
                <FieldError errors={[fieldState.error]} />
              </Field>
            )}
          />

          <Controller
            control={form.control}
            name="fundMaxPerformanceFee"
            render={({ field, fieldState }) => (
              <Field data-invalid={fieldState.invalid}>
                <FieldLabel htmlFor="rules-fundMaxPerformanceFee">
                  Taxa de performance máx.
                  <InfoHint label="O que é a taxa de performance">
                    <div className="space-y-1 text-left">
                      <p>
                        É a fatia do lucro extra que o gestor leva: só vale o que a gestora rendeu acima do CDI, o juro
                        de referência do mercado.
                      </p>
                      <p>
                        Ex.: rendeu 15% num ano de CDI a 10%? Os 5 pontos a mais são o lucro extra; com 20%, o gestor
                        leva 1 ponto deles.
                      </p>
                    </div>
                  </InfoHint>
                </FieldLabel>
                <InputGroup>
                  <InputGroupInput
                    {...field}
                    id="rules-fundMaxPerformanceFee"
                    inputMode="decimal"
                    numeric
                    disabled={readOnly}
                    aria-invalid={fieldState.invalid}
                    onChange={(e) => field.onChange(e.target.value.replace(/[^\d,]/g, ""))}
                  />
                  <InputGroupAddon align="inline-end">
                    <InputGroupText>% do que passar do CDI</InputGroupText>
                  </InputGroupAddon>
                </InputGroup>
                <FieldDescription>
                  {performance === null
                    ? "Só sobre o que a gestora render acima do CDI."
                    : `Rendeu 15% num ano de CDI a 10%? Os ${displayDecimal(performance.extraPoints)} pontos a mais são o lucro extra, e ${performanceCap}% dele vai para o gestor.`}
                </FieldDescription>
                <FieldError errors={[fieldState.error]} />
              </Field>
            )}
          />

          <span className="text-xs leading-normal text-muted-foreground">
            Cada gestor escolhe as próprias taxas até esse teto, e os outros jogadores veem as taxas antes de comprar
            cotas.
          </span>
        </div>
      )}
    </div>
  );
}
