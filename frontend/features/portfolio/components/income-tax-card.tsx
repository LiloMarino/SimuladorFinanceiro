import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import {
  Popover,
  PopoverContent,
  PopoverDescription,
  PopoverHeader,
  PopoverTitle,
  PopoverTrigger,
} from "@/shared/components/ui/popover";
import { displayDate, displayMoney, parseLocalDate } from "@/shared/lib/utils/display";
import type { PortfolioState } from "@/types";

const RULES = [
  ["Ações", "15% do lucro · isento se as vendas de ações do mês somarem até R$ 20 mil"],
  ["FII e day trade", "20% do lucro"],
  ["ETF e BDR", "15%, sem isenção"],
] as const;

/** IR da renda variável: o que já saiu, o que vai sair e a régua da isenção do mês. */
export function IncomeTaxCard({ portfolio }: { portfolio: PortfolioState }) {
  const sales = Number(portfolio.month_stock_sales);
  const limit = Number(portfolio.stock_sales_exemption);
  // A régua vai um pouco além do limite para a marca da isenção ficar visível
  const scale = Math.max(sales, limit) * 1.25;
  const overLimit = sales > limit;
  const due = Number(portfolio.income_tax_due) > 0;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Imposto de renda</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4">
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-0.5">
              <span className="text-xs text-muted-foreground">Já pago</span>
              <span className="font-mono font-semibold">{displayMoney(portfolio.income_tax_paid)}</span>
            </div>
            <div className="grid gap-0.5">
              <span className="text-xs text-muted-foreground">A pagar</span>
              <span className={due ? "font-mono font-semibold text-warning" : "font-mono font-semibold"}>
                {displayMoney(portfolio.income_tax_due)}
              </span>
            </div>
          </div>
          {due && portfolio.income_tax_due_date && (
            <p className="text-xs text-muted-foreground">
              Sai do caixa em {displayDate(parseLocalDate(portfolio.income_tax_due_date))}.
            </p>
          )}
          {!due && Number(portfolio.income_tax_paid) === 0 && (
            <p className="text-xs text-muted-foreground">Nenhuma venda com lucro ainda.</p>
          )}

          {/* Régua da isenção */}
          <div className="grid gap-1.5">
            <div className="flex justify-between text-xs">
              <span className="text-muted-foreground">Vendas de ações no mês</span>
              <span className="font-mono">{displayMoney(sales)}</span>
            </div>
            <div className="relative h-1.5 rounded-full bg-muted">
              <span
                className={
                  overLimit
                    ? "absolute inset-y-0 left-0 rounded-full bg-warning"
                    : "absolute inset-y-0 left-0 rounded-full bg-primary"
                }
                style={{ width: `${(sales / scale) * 100}%` }}
              />
              <span
                className="absolute -top-1 h-3.5 w-0.5 bg-foreground"
                style={{ left: `${(limit / scale) * 100}%` }}
              />
            </div>
            <p className="text-xs text-muted-foreground">
              {overLimit
                ? `Passou da isenção de ${displayMoney(limit)} no mês, então o lucro em ações é tributado.`
                : `Até ${displayMoney(limit)} em vendas de ações no mês, o lucro com ações é isento.`}
            </p>
          </div>

          <Popover>
            <PopoverTrigger render={<Button variant="link" size="sm" />}>Como funciona</PopoverTrigger>
            <PopoverContent className="w-[420px]">
              <PopoverHeader>
                <PopoverTitle>Como o IR é calculado</PopoverTitle>
                <PopoverDescription>Lucro apurado por mês, sobre o preço médio.</PopoverDescription>
              </PopoverHeader>
              <dl className="grid gap-2 text-[13px]">
                {RULES.map(([kind, rule]) => (
                  <div key={kind} className="grid grid-cols-[110px_1fr] gap-2">
                    <dt className="font-medium">{kind}</dt>
                    <dd className="text-muted-foreground">{rule}</dd>
                  </div>
                ))}
              </dl>
              <ul className="grid list-disc gap-1 pl-4 text-[13px] text-muted-foreground">
                <li>Prejuízo abate o lucro dos meses seguintes.</li>
                <li>Sai do caixa no último dia útil do mês seguinte; abaixo de R$ 10, soma ao próximo.</li>
              </ul>
            </PopoverContent>
          </Popover>
        </div>
      </CardContent>
    </Card>
  );
}
