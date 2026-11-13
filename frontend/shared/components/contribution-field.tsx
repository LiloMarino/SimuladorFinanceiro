import { Button } from "@/shared/components/ui/button";
import { Field, FieldDescription, FieldError, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { displayMoneyCompact } from "@/shared/lib/utils/display";
import { formatMoney } from "@/shared/lib/utils/format";
import type { ReactNode } from "react";
import { addToContribution, contributionText } from "@/shared/lib/contribution";

const SHORTCUTS = [2000, 5000, 10000];

type ContributionFieldProps = {
  id: string;
  value: string;
  onChange: (value: string) => void;
  /** Explicação sob o campo; some quando há erro */
  note: ReactNode;
  error?: string | null | undefined;
  /** O campo recebe o foco ao abrir o diálogo */
  autoFocus?: boolean;
};

/** "Sua contribuição mensal": campo de valor, atalhos e a nota de como o dinheiro sai. */
export function ContributionField({ id, value, onChange, note, error, autoFocus }: ContributionFieldProps) {
  return (
    <Field data-invalid={!!error}>
      <FieldLabel htmlFor={id}>Sua contribuição mensal</FieldLabel>
      <Input
        id={id}
        autoFocus={autoFocus}
        numeric
        inputMode="decimal"
        placeholder="R$ 0,00"
        value={value}
        aria-invalid={!!error}
        onChange={(event) => onChange(formatMoney(event.target.value))}
      />
      {/* Zerar o campo e atalhos que somam ao valor */}
      <div className="grid grid-cols-4 gap-1.5">
        <Button type="button" size="sm" variant="outline" onClick={() => onChange(contributionText("0"))}>
          R$ 0
        </Button>
        {SHORTCUTS.map((amount) => (
          <Button
            key={amount}
            type="button"
            size="sm"
            variant="outline"
            onClick={() => onChange(addToContribution(value, amount))}
          >
            +{displayMoneyCompact(amount)}
          </Button>
        ))}
      </div>
      {error ? <FieldError>{error}</FieldError> : <FieldDescription>{note}</FieldDescription>}
    </Field>
  );
}
