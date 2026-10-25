import { Button } from "@/shared/components/ui/button";
import { Card, CardAction, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import {
  Popover,
  PopoverContent,
  PopoverDescription,
  PopoverHeader,
  PopoverTitle,
  PopoverTrigger,
} from "@/shared/components/ui/popover";
import { displayDate, displayMoney, parseLocalDate } from "@/shared/lib/utils/display";
import { salesMonthName } from "@/shared/lib/income-tax";
import type { PortfolioState } from "@/types";

const RULES = [
  ["Ações", "15% do lucro · isento se as vendas de ações do mês somarem até R$ 20 mil"],
  ["FII e day trade", "20% do lucro"],
  ["ETF e BDR", "15%, sem isenção"],
  ["Cripto", "15% do lucro · isento se as vendas de cripto do mês somarem até R$ 35 mil"],
] as const;

/** IR da renda variável: o que já saiu, o que vai sair e a régua da isenção do mês. */
export function IncomeTaxCard({ portfolio }: { portfolio: PortfolioState }) {
  // A régua de cripto só aparece no mês em que houve venda dela
  const rulers = [
    { noun: "ações", sales: Number(portfolio.month_stock_sales), limit: Number(portfolio.stock_sales_exemption) },
    { noun: "cripto", sales: Number(portfolio.month_crypto_sales), limit: Number(portfolio.crypto_sales_exemption) },
  ].filter((ruler) => ruler.noun === "ações" || ruler.sales > 0);
  const due = Number(portfolio.income_tax_due) > 0;
  const dueDate = portfolio.income_tax_due_date;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Imposto de renda</CardTitle>
        <CardAction>
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
        </CardAction>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4">
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-0.5">
              <span className="text-xs text-muted-foreground">Já pago</span>
              <span className="font-mono text-lg font-semibold">{displayMoney(portfolio.income_tax_paid)}</span>
            </div>
            <div className="grid gap-0.5">
              <span className="text-xs text-muted-foreground">A pagar</span>
              <span
                className={due ? "font-mono text-lg font-semibold text-warning" : "font-mono text-lg font-semibold"}
              >
                {displayMoney(portfolio.income_tax_due)}
              </span>
            </div>
          </div>
          {due && dueDate && (
            <p className="text-[13px] text-muted-foreground">
              Sai do caixa em <b className="font-mono text-foreground">{displayDate(parseLocalDate(dueDate))}</b>, pelo
              lucro das vendas de {salesMonthName(dueDate)}.
            </p>
          )}
          {!due && Number(portfolio.income_tax_paid) === 0 && (
            <p className="text-[13px] text-muted-foreground">Nenhuma venda com lucro ainda</p>
          )}

          {/* Réguas da isenção */}
          {rulers.map(({ noun, sales, limit }) => {
            // A barra enche com vendas / limite; passando do limite, a marca recua para a posição real dele
            const scale = Math.max(sales, limit) || 1;
            const overLimit = sales > limit;
            return (
              <div key={noun} className="grid gap-1.5 border-t border-border pt-3">
                <div className="flex justify-between text-xs">
                  <span className="text-muted-foreground">Vendas de {noun} no mês</span>
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
                    ? `Passou da isenção de ${displayMoney(limit)} no mês, então o lucro em ${noun} é tributado.`
                    : `Até ${displayMoney(limit)} em vendas de ${noun} no mês, o lucro com ${noun} é isento.`}
                </p>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
