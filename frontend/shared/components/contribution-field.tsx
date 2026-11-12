import { Button } from "@/shared/components/ui/button";
import { Field, FieldDescription, FieldError, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { displayMoney, displayMoneyCompact } from "@/shared/lib/utils/display";
import { formatMoney } from "@/shared/lib/utils/format";
import type { ReactNode } from "react";
import { addToContribution, contributionAmount, contributionText } from "@/shared/lib/contribution";

const SHORTCUTS = [1000, 2000, 5000];

type ContributionFieldProps = {
  id: string;
  value: string;
  onChange: (value: string) => void;
  /** Explicação sob o campo; some quando há erro */
  note: ReactNode;
  /** O teto da contribuição de cada pessoa por mês, de hoje, em reais */
  cap: string;
  error?: string | null | undefined;
  /** O campo recebe o foco ao abrir o diálogo */
  autoFocus?: boolean;
};

/** "Sua contribuição mensal": campo de valor, atalhos e a nota de como o dinheiro sai. */
export function ContributionField({ id, value, onChange, note, cap, error, autoFocus }: ContributionFieldProps) {
  const capError =
    Number(contributionAmount(value)) > Number(cap) ? `O teto é ${displayMoney(cap)} por pessoa ao mês.` : null;
  const shown = capError ?? error;

  return (
    <Field data-invalid={!!shown}>
      <FieldLabel htmlFor={id}>Sua contribuição mensal</FieldLabel>
      <Input
        id={id}
        autoFocus={autoFocus}
        numeric
        inputMode="decimal"
        placeholder="R$ 0,00"
        value={value}
        aria-invalid={!!shown}
        onChange={(event) => onChange(formatMoney(event.target.value))}
      />
      <div className="flex flex-wrap gap-1.5">
        {/* Zerar o campo e atalhos que somam ao valor */}
        <Button type="button" size="xs" variant="outline" onClick={() => onChange(contributionText("0"))}>
          R$ 0
        </Button>
        {SHORTCUTS.map((amount) => (
          <Button
            key={amount}
            type="button"
            size="xs"
            variant="outline"
            onClick={() => onChange(addToContribution(value, amount))}
          >
            {displayMoneyCompact(amount)}
          </Button>
        ))}
      </div>
      {shown ? (
        <FieldError>{shown}</FieldError>
      ) : (
        <FieldDescription>
          {note} Teto de {displayMoney(cap)} por pessoa ao mês.
        </FieldDescription>
      )}
    </Field>
  );
}
