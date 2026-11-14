import { Button } from "@/shared/components/ui/button";
import { Checkbox } from "@/shared/components/ui/checkbox";
import { Field, FieldDescription, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { displayMoney, displayQuantity } from "@/shared/lib/utils/display";
import { formatMoney, formatPositiveInteger } from "@/shared/lib/utils/format";
import { moneyToField } from "@/shared/lib/utils/money-field";
import type { PortfolioState } from "@/types";
import { cashOf, freeSize, pickedQuantity, type StockPicks } from "../lib/fund-contribution";

type ContributionPickerProps = {
  portfolio: PortfolioState;
  cashText: string;
  onCashChange: (value: string) => void;
  picks: StockPicks;
  onPicksChange: (picks: StockPicks) => void;
  idPrefix: string;
};

/** O que sai da carteira para a gestora: caixa e ações (os títulos ficam de fora). */
export function ContributionPicker({
  portfolio,
  cashText,
  onCashChange,
  picks,
  onPicksChange,
  idPrefix,
}: ContributionPickerProps) {
  const cashTooHigh = cashOf(cashText) > Number(portfolio.cash) + 1e-9;
  const positions = portfolio.variable_income.filter((position) => freeSize(position) > 0);

  const toggle = (ticker: string, checked: boolean, free: number) => {
    const rest = Object.fromEntries(Object.entries(picks).filter(([picked]) => picked !== ticker));
    onPicksChange(checked ? { ...rest, [ticker]: String(free) } : rest);
  };

  return (
    <div className="grid gap-4">
      <Field data-invalid={cashTooHigh}>
        <FieldLabel htmlFor={`${idPrefix}-cash`}>Caixa</FieldLabel>
        <div className="flex gap-2">
          <Input
            id={`${idPrefix}-cash`}
            numeric
            inputMode="decimal"
            placeholder="R$ 0,00"
            value={cashText}
            aria-invalid={cashTooHigh}
            onChange={(event) => onCashChange(formatMoney(event.target.value))}
          />
          <Button type="button" variant="outline" onClick={() => onCashChange(moneyToField(portfolio.cash))}>
            Tudo
          </Button>
        </div>
        <FieldDescription>
          {cashTooHigh ? "Passa do caixa da carteira." : `Você tem ${displayMoney(portfolio.cash)} em caixa.`}
        </FieldDescription>
      </Field>

      <div className="grid gap-1.5">
        <span className="text-sm font-medium">Ações</span>
        {positions.length === 0 ? (
          <p className="text-[13px] text-muted-foreground">A carteira não tem ações livres para levar.</p>
        ) : (
          <ul className="grid rounded-lg border border-border">
            {positions.map((position) => {
              const checked = position.ticker in picks;
              const valid = !checked || pickedQuantity(picks[position.ticker], position) > 0;
              return (
                <li
                  key={position.ticker}
                  className="grid grid-cols-[auto_1fr_7rem] items-center gap-3 border-t border-muted px-3 py-2 first:border-t-0"
                >
                  <Checkbox
                    aria-label={`Levar ${position.ticker}`}
                    checked={checked}
                    onCheckedChange={(next) => toggle(position.ticker, next === true, freeSize(position))}
                  />
                  <span className="grid min-w-0 text-[13px]">
                    <b className="font-semibold">{position.ticker}</b>
                    <span className="truncate text-xs text-muted-foreground">
                      {displayQuantity(String(freeSize(position)))} livres · {displayMoney(position.current_price)} cada
                    </span>
                  </span>
                  <Input
                    numeric
                    inputMode="numeric"
                    aria-label={`Quantidade de ${position.ticker}`}
                    aria-invalid={!valid}
                    disabled={!checked}
                    value={picks[position.ticker] ?? ""}
                    onChange={(event) =>
                      onPicksChange({ ...picks, [position.ticker]: formatPositiveInteger(event.target.value) })
                    }
                  />
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </div>
  );
}
