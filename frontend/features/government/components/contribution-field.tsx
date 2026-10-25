import { Button } from "@/shared/components/ui/button";
import { Field, FieldDescription, FieldError, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { displayMoneyCompact } from "@/shared/lib/utils/display";
import { formatMoney } from "@/shared/lib/utils/format";
import type { ReactNode } from "react";
import { contributionAmount, contributionText } from "../lib/contribution";

const SHORTCUTS = [0, 2000, 5000, 10000];

type ContributionFieldProps = {
  id: string;
  value: string;
  onChange: (value: string) => void;
  /** Explicação sob o campo; some quando há erro */
  note: ReactNode;
  error?: string | null;
};

/** "Sua contribuição mensal": campo de valor, atalhos e a nota de como o dinheiro sai. */
export function ContributionField({ id, value, onChange, note, error }: ContributionFieldProps) {
  return (
    <Field data-invalid={!!error}>
      <FieldLabel htmlFor={id}>Sua contribuição mensal</FieldLabel>
      <Input
        id={id}
        numeric
        inputMode="decimal"
        placeholder="R$ 0,00"
        value={value}
        aria-invalid={!!error}
        onChange={(event) => onChange(formatMoney(event.target.value))}
      />
      <div className="flex flex-wrap gap-1.5">
        {SHORTCUTS.map((amount) => (
          <Button
            key={amount}
            type="button"
            size="xs"
            variant={
              contributionAmount(value) === contributionAmount(contributionText(String(amount))) ? "info" : "outline"
            }
            onClick={() => onChange(contributionText(String(amount)))}
          >
            {amount === 0 ? "R$ 0" : displayMoneyCompact(amount)}
          </Button>
        ))}
      </div>
      {error ? <FieldError>{error}</FieldError> : <FieldDescription>{note}</FieldDescription>}
    </Field>
  );
}
