import { Controller, type Control } from "react-hook-form";
import { Check } from "lucide-react";
import { Field, FieldDescription, FieldError, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { PARTY_COLORS } from "@/shared/lib/party-colors";
import { cn } from "@/shared/lib/utils";
import type { PartyIdentity } from "@/types";

type PartyIdentityFieldsProps = {
  control: Control<PartyIdentity>;
  /** Cores que outros partidos já usam */
  takenColors: string[];
  /** Prefixo dos ids, para dois formulários na mesma tela não repetirem */
  idPrefix: string;
};

/** Nome, sigla e cor do partido; as bandeiras ficam com quem usa. */
export function PartyIdentityFields({ control, takenColors, idPrefix }: PartyIdentityFieldsProps) {
  const taken = new Set(takenColors.map((color) => color.toUpperCase()));
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
            <div role="radiogroup" aria-label="Cor do partido" className="flex flex-wrap gap-2">
              {PARTY_COLORS.map((color) => {
                const used = taken.has(color);
                const selected = field.value === color;
                return (
                  <button
                    key={color}
                    type="button"
                    role="radio"
                    aria-checked={selected}
                    aria-label={used ? `${color}, já usada` : color}
                    disabled={used}
                    onClick={() => field.onChange(color)}
                    className={cn(
                      "inline-flex size-6.5 items-center justify-center rounded-[7px] text-white outline-none focus-visible:ring-3 focus-visible:ring-ring/50",
                      selected && "ring-2 ring-foreground ring-offset-2 ring-offset-card",
                      used && "opacity-25",
                    )}
                    style={{ backgroundColor: color }}
                  >
                    {used && <Check className="size-3.5" />}
                  </button>
                );
              })}
            </div>
            <FieldDescription>Cada partido tem uma cor; o cinza é dos partidos do computador.</FieldDescription>
          </Field>
        )}
      />
    </>
  );
}
