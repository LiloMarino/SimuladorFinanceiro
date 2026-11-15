import { PartyMark } from "@/shared/components/party-mark";
import { cn } from "@/shared/lib/utils";

export type PartyOption = {
  abbr: string;
  /** Nulo no partido do computador, que tem a cor fixa da sigla */
  color: string | null;
};

type CommissionedPartyPickerProps = {
  options: PartyOption[];
  /** A sigla marcada; nula enquanto o jogador não escolheu */
  value: string | null | undefined;
  disabled?: boolean;
  onChange: (abbr: string) => void;
};

/** O partido do Comissionado: a renda sobe com ele no governo (presidência ou base) e cai fora dele. */
export function CommissionedPartyPicker({ options, value, disabled, onChange }: CommissionedPartyPickerProps) {
  return (
    <div className="grid gap-2">
      <span className="text-xs font-semibold text-muted-foreground">Partido do Comissionado</span>
      <div role="radiogroup" aria-label="Partido do Comissionado" className="flex flex-wrap gap-2">
        {options.map((option) => (
          <button
            key={option.abbr}
            type="button"
            role="radio"
            aria-checked={option.abbr === value}
            disabled={disabled}
            onClick={() => onChange(option.abbr)}
            className={cn(
              "cursor-pointer rounded-lg border p-1.5 outline-none focus-visible:ring-3 focus-visible:ring-ring/50 disabled:cursor-default disabled:opacity-55",
              option.abbr === value && "bg-subtle ring-2 ring-foreground",
            )}
          >
            <PartyMark abbr={option.abbr} color={option.color} />
          </button>
        ))}
      </div>
      <span className="text-xs text-muted-foreground">
        Com o partido na presidência ou na base do governo, a renda é 1,5× o salário; fora dele, 0,5×. A troca de
        governo vale a partir do mês seguinte.
      </span>
    </div>
  );
}
