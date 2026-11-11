import { Controller, type Control } from "react-hook-form";
import { ColorSwatchPicker } from "@/shared/components/color-swatch-picker";
import { Field, FieldDescription, FieldError, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { PARTY_PALETTE } from "@/shared/lib/party-colors";
import type { PartyIdentity } from "@/types";

/** Uma cor que outro partido já usa e a sigla dele. */
export type PartyTakenColor = { color: string; abbr: string };

type PartyIdentityFieldsProps = {
  control: Control<PartyIdentity>;
  /** Cores que outros partidos já usam, com a sigla de cada um */
  taken: PartyTakenColor[];
  /** Prefixo dos ids, para dois formulários na mesma tela não repetirem */
  idPrefix: string;
};

/** Nome, sigla e cor do partido; as bandeiras ficam com quem usa. */
export function PartyIdentityFields({ control, taken, idPrefix }: PartyIdentityFieldsProps) {
  return (
    <>
      <div className="grid grid-cols-[1fr_7rem] gap-3">
        <Controller
          control={control}
          name="name"
          render={({ field, fieldState }) => (
            <Field data-invalid={fieldState.invalid}>
              <FieldLabel htmlFor={`${idPrefix}-name`}>Nome</FieldLabel>
              <Input id={`${idPrefix}-name`} autoComplete="off" aria-invalid={fieldState.invalid} {...field} />
              <FieldError errors={[fieldState.error]} />
            </Field>
          )}
        />
        <Controller
          control={control}
          name="abbr"
          render={({ field, fieldState }) => (
            <Field data-invalid={fieldState.invalid}>
              <FieldLabel htmlFor={`${idPrefix}-abbr`}>Sigla</FieldLabel>
              <Input
                id={`${idPrefix}-abbr`}
                numeric
                autoComplete="off"
                maxLength={8}
                aria-invalid={fieldState.invalid}
                {...field}
                onChange={(event) => field.onChange(event.target.value.toUpperCase().replace(/[^A-ZÀ-Ý]/g, ""))}
              />
              {fieldState.error ? (
                <FieldError errors={[fieldState.error]} />
              ) : (
                <FieldDescription>2 a 8 letras.</FieldDescription>
              )}
            </Field>
          )}
        />
      </div>

      <Controller
        control={control}
        name="color"
        render={({ field }) => (
          <Field>
            <FieldLabel>Cor</FieldLabel>
            <ColorSwatchPicker
              colors={PARTY_PALETTE}
              taken={taken.map((party) => ({ color: party.color, label: party.abbr, owner: party.abbr }))}
              value={field.value}
              onChange={field.onChange}
              columns={10}
              label="Cor do partido"
            />
            <FieldDescription>Cada partido tem uma cor própria.</FieldDescription>
          </Field>
        )}
      />
    </>
  );
}
