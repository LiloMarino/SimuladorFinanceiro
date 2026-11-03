import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { cn } from "@/shared/lib/utils";
import { displayDayMonth, displayMoney, displayMonthShort } from "@/shared/lib/utils/display";
import type { CreditOverview } from "@/types";

type PaymentsCardProps = { overview: CreditOverview };

// Pontos por parcela no mês; passa disso, os pontos ficam só na contagem do tooltip
const MAX_DOTS = 3;

const LEGEND = [
  { label: "Paga em dia", dot: "bg-success" },
  { label: "Paga com atraso", dot: "bg-warning" },
  { label: "Em atraso", dot: "bg-destructive" },
];

/** "Pagamentos": as próximas parcelas e os últimos 12 meses de pontualidade. */
export function PaymentsCard({ overview }: PaymentsCardProps) {
  // As parcelas em atraso abrem a lista, da mais antiga para a mais recente
  const overdue = overview.loans
    .flatMap((loan) => loan.overdue.map((item) => ({ loan, item })))
    .sort((a, b) => a.item.due_date.localeCompare(b.item.due_date));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Pagamentos</CardTitle>
        <CardDescription>As próximas parcelas e os últimos 12 meses</CardDescription>
      </CardHeader>

      <CardContent>
        <div className="grid gap-4">
          {/* Próximas parcelas */}
          {overdue.length > 0 || overview.upcoming.length > 0 ? (
            <div>
              {overdue.map(({ loan, item }) => (
                <div
                  key={`late-${loan.number}-${item.installment_number}`}
                  className="flex justify-between gap-3 border-t border-muted py-1.75 text-[13px] first:border-t-0"
                >
                  <span>
                    <span className="font-mono font-semibold text-destructive">{displayDayMonth(item.due_date)}</span>{" "}
                    <span className="text-muted-foreground">
                      · Empréstimo {loan.number} · {item.installment_number} de {loan.total_installments}
                    </span>{" "}
                    <span className="font-semibold text-destructive">
                      Em atraso há {item.days_late} {item.days_late === 1 ? "dia" : "dias"}
                    </span>
                  </span>
                  <span className="font-mono text-destructive">{displayMoney(item.total)}</span>
                </div>
              ))}
              {overview.upcoming.map((item) => (
                <div
                  key={`${item.loan_number}-${item.installment_number}`}
                  className="flex justify-between gap-3 border-t border-muted py-1.75 text-[13px] first:border-t-0"
                >
                  <span>
                    <span className="font-mono font-semibold">{displayDayMonth(item.due_date)}</span>{" "}
                    <span className="text-muted-foreground">
                      · Empréstimo {item.loan_number} · {item.installment_number} de {item.total_installments}
                    </span>
                  </span>
                  <span className="font-mono">{displayMoney(item.amount)}</span>
                </div>
              ))}
            </div>
          ) : (
            <span className="text-[13px] text-muted-foreground">Nenhuma parcela a vencer.</span>
          )}

          {/* Histórico */}
          <div className="grid gap-2">
            <span className="text-[13px] font-medium">Histórico</span>
            <ol className="grid grid-cols-12 gap-1.5">
              {overview.history.map((month) => {
                const total = month.on_time + month.paid_late + month.late;
                const tone =
                  month.late > 0
                    ? "bg-destructive-soft"
                    : month.paid_late > 0
                      ? "bg-warning-soft"
                      : total > 0
                        ? "bg-success-soft"
                        : "bg-subtle";
                const dots = [
                  ...Array<string>(month.on_time).fill("bg-success"),
                  ...Array<string>(month.paid_late).fill("bg-warning"),
                  ...Array<string>(month.late).fill("bg-destructive"),
                ].slice(0, MAX_DOTS);
                return (
                  <li key={month.month} className="grid justify-items-center gap-1 text-[11px] text-faint-foreground">
                    <span
                      className={cn("flex h-7 w-full items-center justify-center gap-0.75 rounded-md", tone)}
                      title={
                        total === 0
                          ? "Sem parcela no mês"
                          : `${month.on_time} em dia, ${month.paid_late} com atraso, ${month.late} em atraso`
                      }
                    >
                      {dots.map((dot, index) => (
                        <span key={index} className={cn("size-2 rounded-full", dot)} />
                      ))}
                    </span>
                    {displayMonthShort(month.month)}
                    {month.late > 0 && <span className="font-semibold text-destructive">Atraso</span>}
                  </li>
                );
              })}
            </ol>
            <ul className="flex flex-wrap gap-x-3.5 gap-y-1 text-xs text-muted-foreground">
              {LEGEND.map((item) => (
                <li key={item.label} className="flex items-center gap-1.5">
                  <span className={cn("size-2.5 rounded-[3px]", item.dot)} aria-hidden="true" />
                  {item.label}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
