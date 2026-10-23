import { Info } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { displayWholePercent } from "@/shared/lib/credit";
import { displayMoneyCompact } from "@/shared/lib/utils/display";
import type { CreditOverview } from "@/types";
import { CreditGradeMark } from "./credit-grade-mark";

type BlockedRatingCardProps = {
  overview: CreditOverview;
  /** Há parcela em atraso para pagar já */
  onPayOverdue: (() => void) | null;
};

/** Nota D: o crédito novo fica fechado e o caminho de volta aparece no lugar da oferta. */
export function BlockedRatingCard({ overview, onPayOverdue }: BlockedRatingCardProps) {
  const { rating } = overview;
  const recover = overview.suggestions.find((item) => item.kind === "RECOVER");
  const recoverTier = rating.ladder.find((tier) => tier.grade === recover?.target_grade);
  const late = rating.payments.late_installments;

  const causes = [
    late > 0 && `${late} ${late === 1 ? "parcela atrasou" : "parcelas atrasaram"} em 12 meses`,
    overview.leverage !== null &&
      Number(overview.leverage) > 0 &&
      `a dívida está em ${displayWholePercent(overview.leverage)} do patrimônio`,
  ].filter(Boolean);

  return (
    <Card>
      <CardContent>
        <div className="grid gap-3.5">
          <div className="flex items-center gap-4">
            <CreditGradeMark grade={rating.grade} size="md" />
            <div className="grid gap-0.5">
              <b className="text-[15px] font-semibold">Sem crédito novo com a nota {rating.grade}</b>
              <span className="text-[13px] text-muted-foreground">
                {rating.points} pontos{causes.length > 0 && `: ${causes.join(" e ")}`}. Os empréstimos que você já tem
                seguem com o juro travado.
              </span>
            </div>
          </div>

          {recover && (
            <Alert variant="info" className="has-[>svg]:grid-cols-[auto_1fr_auto]">
              <Info />
              <AlertTitle>
                Para voltar a ter crédito ({recover.target_grade}
                {recoverTier ? `, ${recoverTier.min_points} pontos` : ""})
              </AlertTitle>
              {onPayOverdue && (
                <span className="row-span-2 self-center">
                  <Button size="sm" onClick={onPayOverdue}>
                    Pagar o atraso
                  </Button>
                </span>
              )}
              <AlertDescription>
                {onPayOverdue ? "Pague a parcela em atraso e quite" : "Quite"} {displayMoneyCompact(recover.amount ?? 0)}: a
                alavancagem cai para {displayWholePercent(recover.leverage_after ?? 0)}. A nota muda no fim do mês.
              </AlertDescription>
            </Alert>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
