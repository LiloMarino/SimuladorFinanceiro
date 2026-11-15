import { Controller, useWatch, type UseFormReturn } from "react-hook-form";
import { Field, FieldDescription, FieldError, FieldLabel } from "@/shared/components/ui/field";
import { InfoHint } from "@/shared/components/info-hint";
import { InputGroup, InputGroupAddon, InputGroupInput, InputGroupText } from "@/shared/components/ui/input-group";
import { Switch } from "@/shared/components/ui/switch";
import { EXPANSIONS } from "@/shared/lib/expansions";
import { displayDecimal, displayMoneyWhole } from "@/shared/lib/utils/display";
import { cn } from "@/shared/lib/utils";
import { managementFeeExample, managerMaxShare, performanceFeeExample } from "../lib/fund-rules";
import type { SimulationFormValues } from "../lib/simulation-form";
import { ExpansionIntro } from "./expansion-intro";

const FUNDS = EXPANSIONS.funds;

type FundsCardProps = {
  form: UseFormReturn<SimulationFormValues>;
  /** Sem edição: convidado ou regras de uma partida salva */
  readOnly: boolean;
};

/** O cartão "Gestoras": a chave da expansão, os tetos das taxas e o modo aquisição hostil. */
export function FundsCard({ form, readOnly }: FundsCardProps) {
  const [enabled, managementCap, performanceCap, takeover, minMarketShare] = useWatch({
    control: form.control,
    name: [
      "fundsEnabled",
      "fundMaxManagementFee",
      "fundMaxPerformanceFee",
      "fundTakeoverEnabled",
      "fundMinMarketShare",
    ],
  });
  const monthlyFee = managementFeeExample(managementCap);
  const performance = performanceFeeExample(performanceCap);
  const managerShare = managerMaxShare(minMarketShare);

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

      {/* Modo aquisição hostil */}
      {enabled && (
        <div className="grid gap-3.5 border-t px-4 py-3.5">
          <Controller
            control={form.control}
            name="fundTakeoverEnabled"
            render={({ field }) => (
              <div className="flex items-start justify-between gap-3">
                <div className="grid gap-0.5">
                  <span className="flex items-center text-sm font-medium">
                    Modo aquisição hostil
                    <InfoHint label="O que é o modo aquisição hostil">
                      <div className="space-y-1 text-left">
                        <p>
                          Todos começam com a carteira inteira dentro da própria gestora. Quem perde a assembleia de
                          troca de gestor sai da partida e passa a só assistir.
                        </p>
                        <p>A partida termina quando sobra uma gestora com jogador ativo.</p>
                      </div>
                    </InfoHint>
                  </span>
                  <span className="text-xs leading-normal text-muted-foreground">
                    Perder a assembleia tira o dono da partida.
                  </span>
                </div>
                <Switch
                  aria-label="Ligar o modo aquisição hostil"
                  checked={field.value}
                  disabled={readOnly}
                  onCheckedChange={field.onChange}
                />
              </div>
            )}
          />

          {takeover && (
            <>
              <Controller
                control={form.control}
                name="fundGraceMonths"
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="rules-fundGraceMonths">
                      Carência (meses)
                      <InfoHint label="O que é a carência">
                        <div className="space-y-1 text-left">
                          <p>
                            É o tempo, desde o início da partida, em que ninguém pode convocar a assembleia de troca de
                            gestor.
                          </p>
                          <p>
                            Ex.: com 12 meses e início em 01/01, a assembleia só abre a partir de 01/01 do ano seguinte.
                          </p>
                        </div>
                      </InfoHint>
                    </FieldLabel>
                    <InputGroup>
                      <InputGroupInput
                        {...field}
                        id="rules-fundGraceMonths"
                        inputMode="numeric"
                        numeric
                        disabled={readOnly}
                        aria-invalid={fieldState.invalid}
                        onChange={(e) => field.onChange(e.target.value.replace(/\D/g, ""))}
                      />
                      <InputGroupAddon align="inline-end">
                        <InputGroupText>meses</InputGroupText>
                      </InputGroupAddon>
                    </InputGroup>
                    <FieldDescription>Sem assembleia até o fim da carência.</FieldDescription>
                    <FieldError errors={[fieldState.error]} />
                  </Field>
                )}
              />

              <Controller
                control={form.control}
                name="fundMinMarketShare"
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="rules-fundMinMarketShare">
                      Mínimo de cotas no mercado (%)
                      <InfoHint label="O que é o mínimo de cotas no mercado">
                        <div className="space-y-1 text-left">
                          <p>
                            É a fatia das cotas de cada gestora que precisa estar com outros investidores quando a
                            carência acaba. O que o gestor tem acima do limite é posto à venda pelo patrimônio por cota.
                          </p>
                          <p>
                            Ex.: com 50%, o gestor de uma gestora de 1.000 cotas fica com no máximo 500; se ele tinha
                            800, as 300 a mais vão à venda.
                          </p>
                        </div>
                      </InfoHint>
                    </FieldLabel>
                    <InputGroup>
                      <InputGroupInput
                        {...field}
                        id="rules-fundMinMarketShare"
                        inputMode="decimal"
                        numeric
                        disabled={readOnly}
                        aria-invalid={fieldState.invalid}
                        onChange={(e) => field.onChange(e.target.value.replace(/[^\d,]/g, ""))}
                      />
                      <InputGroupAddon align="inline-end">
                        <InputGroupText>% das cotas</InputGroupText>
                      </InputGroupAddon>
                    </InputGroup>
                    <FieldDescription>
                      {managerShare === null
                        ? "Fatia das cotas que fica com o mercado ao fim da carência."
                        : `O gestor pode manter até ${displayDecimal(managerShare)}% das cotas da própria gestora.`}
                    </FieldDescription>
                    <FieldError errors={[fieldState.error]} />
                  </Field>
                )}
              />
            </>
          )}
        </div>
      )}
    </div>
  );
}
