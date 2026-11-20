import { Controller, useWatch, type UseFormReturn } from "react-hook-form";
import { FUND_TAKEOVER_GAME_TYPE } from "@/shared/lib/game-types";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";
import { Field, FieldDescription, FieldError, FieldLabel } from "@/shared/components/ui/field";
import { InfoHint } from "@/shared/components/info-hint";
import { InputGroup, InputGroupAddon, InputGroupInput, InputGroupText } from "@/shared/components/ui/input-group";
import { displayDecimal, displayIsoDate } from "@/shared/lib/utils/display";
import { graceOpening, managerMaxShare } from "../../lib/fund-rules";
import type { SimulationFormValues } from "../../lib/simulation-form";

type TakeoverFieldsProps = {
  form: UseFormReturn<SimulationFormValues>;
  readOnly: boolean;
};

/** A carência, o mínimo de cotas no mercado e o aviso de quem vence na aquisição hostil. */
export function TakeoverFields({ form, readOnly }: TakeoverFieldsProps) {
  const [startDate, graceMonths, minMarketShare] = useWatch({
    control: form.control,
    name: ["startDate", "fundGraceMonths", "fundMinMarketShare"],
  });
  const opening = graceOpening(startDate, graceMonths);
  const managerShare = managerMaxShare(minMarketShare);

  return (
    <>
      <div className="grid gap-3 rounded-[10px] bg-subtle px-3.5 py-3">
        {/* Carência */}
        <Controller
          control={form.control}
          name="fundGraceMonths"
          render={({ field, fieldState }) => (
            <Field data-invalid={fieldState.invalid}>
              <FieldLabel htmlFor="rules-fundGraceMonths">
                Carência
                <InfoHint label="O que é a carência">
                  <div className="space-y-1 text-left">
                    <p>
                      É o tempo, desde o início da partida, em que ninguém pode convocar a assembleia de troca de
                      gestor.
                    </p>
                    <p>Ex.: com 12 meses e início em 01/01, a assembleia só abre a partir de 01/01 do ano seguinte.</p>
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
              <FieldDescription>
                {opening === null
                  ? "Ninguém convoca a assembleia de troca de gestor antes do fim da carência."
                  : `Ninguém convoca a assembleia de troca de gestor antes: com início em ${displayIsoDate(startDate)}, ela abre em ${displayIsoDate(opening)}.`}
              </FieldDescription>
              <FieldError errors={[fieldState.error]} />
            </Field>
          )}
        />

        {/* Mínimo de cotas no mercado */}
        <Controller
          control={form.control}
          name="fundMinMarketShare"
          render={({ field, fieldState }) => (
            <Field data-invalid={fieldState.invalid}>
              <FieldLabel htmlFor="rules-fundMinMarketShare">
                Mínimo de cotas no mercado
                <InfoHint label="O que é o mínimo de cotas no mercado">
                  <div className="space-y-1 text-left">
                    <p>
                      É a fatia das cotas de cada gestora que precisa estar com outros investidores quando a carência
                      acaba. O que o gestor tem acima do limite é posto à venda pelo patrimônio por cota.
                    </p>
                    <p>
                      Ex.: com 50%, o gestor de uma gestora de 1.000 cotas fica com no máximo 500; se ele tinha 800, as
                      300 a mais vão à venda.
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
                  <InputGroupText>%</InputGroupText>
                </InputGroupAddon>
              </InputGroup>
              <FieldDescription>
                {managerShare === null
                  ? "Fatia das cotas que fica com o mercado ao fim da carência."
                  : `Com ${minMarketShare}%, o gestor de 1.000 cotas fica com até ${displayDecimal(managerShare * 10)}; se tinha todas, as ${displayDecimal((100 - managerShare) * 10)} restantes vão à venda.`}
              </FieldDescription>
              <FieldError errors={[fieldState.error]} />
            </Field>
          )}
        />
      </div>

      {/* Como se vence */}
      <Alert variant="info">
        <FUND_TAKEOVER_GAME_TYPE.icon />
        <AlertDescription>
          <b className="font-semibold">Como se vence:</b> quem perde para a assembleia a gestora que fundou sai da
          partida e passa a assistir. A partida acaba quando sobra um jogador; se a data final chegar com mais de um de
          pé, vence o maior patrimônio do ranking.
        </AlertDescription>
      </Alert>
    </>
  );
}
