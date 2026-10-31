import { useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { ErrorState } from "@/shared/components/error-state";
import { Card, CardContent } from "@/shared/components/ui/card";
import usePageLabel from "@/shared/hooks/usePageLabel";
import { PAY_OVERDUE_PARAM } from "@/shared/lib/credit";
import type { CreditLoan, CreditOverview } from "@/types";
import { BlockedRatingCard } from "../components/blocked-rating-card";
import { CreditEmpty } from "../components/credit-empty";
import { CreditSkeleton } from "../components/credit-skeleton";
import { CreditSummary } from "../components/credit-summary";
import { LoanOfferCard } from "../components/loan-offer-card";
import { LoansTable } from "../components/loans-table";
import { PayOverdueDialog } from "../components/pay-overdue-dialog";
import { PaymentsCard } from "../components/payments-card";
import { PrepayDialog, type PrepayChoice } from "../components/prepay-dialog";
import { RatingSuggestionsCard } from "../components/rating-suggestions-card";
import { RiskRatingCard } from "../components/risk-rating-card";
import { useCredit } from "../hooks/queries/useCredit";

export default function CreditPage() {
  usePageLabel("Crédito");
  const { data: overview, error, refetch } = useCredit();

  if (!overview) {
    return error ? (
      <Card>
        <CardContent>
          <ErrorState title="Não deu para carregar o crédito" error={error} onRetry={() => void refetch()} />
        </CardContent>
      </Card>
    ) : (
      <CreditSkeleton />
    );
  }

  return <CreditContent overview={overview} />;
}

type PrepayTarget = { loanId: string; choice: PrepayChoice; amount?: string };

function CreditContent({ overview }: { overview: CreditOverview }) {
  const [params, setParams] = useSearchParams();
  const [prepay, setPrepay] = useState<PrepayTarget | null>(null);
  const amountInput = useRef<HTMLInputElement>(null);

  const { loans, offer, rating } = overview;
  const prepayLoan = loans.find((loan) => loan.id === prepay?.loanId);
  const overdueLoan = loans.find((loan) => loan.id === params.get(PAY_OVERDUE_PARAM) && loan.overdue.length > 0);
  const firstOverdue = loans.find((loan) => loan.overdue.length > 0);
  // As sugestões de amortização miram o empréstimo de juro mais alto, o que mais poupa
  const priciestLoan = [...loans].sort((a, b) => Number(b.annual_rate) - Number(a.annual_rate))[0];

  const openOverdue = (loan: CreditLoan) => setParams({ [PAY_OVERDUE_PARAM]: loan.id }, { replace: true });
  const closeOverdue = () => setParams({}, { replace: true });

  const simulate = () => {
    amountInput.current?.scrollIntoView({ behavior: "smooth", block: "center" });
    amountInput.current?.focus();
  };

  const openOffer =
    offer.available && offer.spread !== null && offer.annual_rate !== null
      ? { spread: offer.spread, annualRate: offer.annual_rate }
      : null;

  return (
    <>
      <CreditSummary overview={overview} />

      {/* Nota de risco e novo empréstimo */}
      <div className="grid items-start gap-5 xl:grid-cols-[1fr_1.3fr]">
        <RiskRatingCard rating={rating} />
        {openOffer ? (
          // A cada empréstimo aberto ou quitado o formulário nasce de novo, com o valor padrão do limite que sobrou
          <LoanOfferCard key={loans.length} overview={overview} {...openOffer} amountInputRef={amountInput} />
        ) : (
          <BlockedRatingCard overview={overview} onPayOverdue={firstOverdue ? () => openOverdue(firstOverdue) : null} />
        )}
      </div>

      {/* Seus empréstimos */}
      {loans.length > 0 ? (
        <LoansTable
          loans={loans}
          onPrepay={(loan, choice) => setPrepay({ loanId: loan.id, choice })}
          onPayOverdue={openOverdue}
        />
      ) : (
        <CreditEmpty overview={overview} onSimulate={simulate} />
      )}

      {/* Pagamentos e como subir a nota */}
      <div className="grid items-start gap-5 xl:grid-cols-[1.3fr_1fr]">
        <PaymentsCard overview={overview} />
        <RatingSuggestionsCard
          overview={overview}
          onAmortize={(amount) => priciestLoan && setPrepay({ loanId: priciestLoan.id, choice: "part", amount })}
        />
      </div>

      {prepayLoan && prepay && (
        <PrepayDialog
          key={`${prepayLoan.id}-${prepay.choice}-${prepay.amount ?? ""}`}
          loan={prepayLoan}
          open
          onOpenChange={() => setPrepay(null)}
          initialChoice={prepay.choice}
          initialAmount={prepay.amount}
        />
      )}
      {overdueLoan && (
        <PayOverdueDialog loan={overdueLoan} rating={rating} cash={overview.cash} open onOpenChange={closeOverdue} />
      )}
    </>
  );
}
