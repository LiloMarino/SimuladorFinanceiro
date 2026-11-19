import { TriangleAlert } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import {
  Dialog,
  DialogBody,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/shared/components/ui/dialog";
import { TradeLockNotice } from "@/shared/components/trade-lock-notice";
import { useTradeLock } from "@/shared/hooks/useTradeLock";
import { displayPercent, displayMoney, displayMonthName } from "@/shared/lib/utils/display";
import { displayLeverage } from "@/shared/lib/credit-metrics";
import type { CreditOverview, LoanQuote } from "@/types";
import { useContractLoan } from "../hooks/mutations/useContractLoan";
import { InstallmentsTable } from "./installments-table";
import { KeyValueRow } from "@/shared/components/key-value-row";

type ReviewLoanDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  quote: LoanQuote;
  rating: CreditOverview["rating"];
};

/** "Revisar o empréstimo": o custo inteiro à vista antes da assinatura. */
export function ReviewLoanDialog({ open, onOpenChange, quote, rating }: ReviewLoanDialogProps) {
  const contract = useContractLoan();
  const tradeLock = useTradeLock();

  const sign = () =>
    contract.mutate({ amount: quote.amount, term_months: quote.term_months }, { onSuccess: () => onOpenChange(false) });

  // A gestora devolve primeiro a taxa a pagar: o quote traz os campos só nessa conta
  const fundQuote =
    quote.fee_payable_settled !== null && quote.first_month_interest_per_quota !== null
      ? { settled: quote.fee_payable_settled, interestPerQuota: quote.first_month_interest_per_quota }
      : null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-130">
        <DialogHeader variant="divided">
          <DialogTitle>Revisar o empréstimo</DialogTitle>
          <DialogDescription>Confira antes de assinar. Depois, só quitando.</DialogDescription>
        </DialogHeader>

        <DialogBody>
          <div className="grid gap-4">
            {/* Condições */}
            <div>
              <KeyValueRow label="Entra no caixa hoje" value={displayMoney(quote.amount)} />
              <KeyValueRow label="Parcela fixa" value={`${quote.term_months} × ${displayMoney(quote.installment)}`} />
              <KeyValueRow label="Juro travado" value={`${displayPercent(quote.annual_rate)} ao ano`} />
              <KeyValueRow label="Juro no prazo todo" value={displayMoney(quote.total_interest)} />
              <KeyValueRow total label="Total a pagar" value={displayMoney(quote.total_paid)} />
            </div>

            {/* Cronograma */}
            <InstallmentsTable schedule={quote.schedule} />
            <span className="-mt-2 text-xs text-muted-foreground">
              A parcela é a mesma; o juro cai e a dívida paga sobe a cada mês.
            </span>

            {/* O que muda na gestora */}
            {fundQuote && (
              <div>
                <KeyValueRow
                  label="Juros no primeiro mês"
                  note={`≈ ${displayMoney(fundQuote.interestPerQuota)} por cota, saídos do patrimônio`}
                  value={`≈ ${displayMoney(quote.schedule[0]?.interest ?? 0)}`}
                />
                <KeyValueRow
                  label="Caixa da gestora depois"
                  note={
                    Number(fundQuote.settled) > 0
                      ? `${displayMoney(fundQuote.settled)} do empréstimo quitam antes a taxa a pagar`
                      : undefined
                  }
                  value={displayMoney(quote.cash_after)}
                />
              </div>
            )}

            {/* Efeito na nota */}
            <div>
              <KeyValueRow
                label={fundQuote ? "Dívida sobre o patrimônio" : "Alavancagem"}
                note={fundQuote ? "A nota é recalculada com a dívida nova" : undefined}
                value={`${displayLeverage(quote.leverage_before)} → ${displayLeverage(quote.leverage_after)}`}
              />
              <KeyValueRow
                label={`Nota no fim de ${displayMonthName(rating.next_review)}`}
                value={`${quote.projected_grade}, com ${quote.projected_points} pontos`}
              />
            </div>

            {/* Estratégia automática ligada */}
            {tradeLock?.reason === "automatic" && <TradeLockNotice lock={tradeLock} />}

            <Alert variant="warning">
              <TriangleAlert />
              <AlertTitle>Sem caixa no dia {quote.due_day}, a parcela atrasa</AlertTitle>
              <AlertDescription>Multa de 2%, mora de 1% ao mês e nota menor. Nada é vendido sozinho.</AlertDescription>
            </Alert>
          </div>
        </DialogBody>

        <DialogFooter variant="divided" className="sm:justify-end">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Voltar
          </Button>
          <Button onClick={sign} disabled={contract.isPending}>
            Assinar contrato
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
