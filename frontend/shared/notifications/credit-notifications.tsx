import { useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { Clock, TrendingUp, TriangleAlert } from "lucide-react";
import { toast } from "sonner";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { displaySelicSpread, displayWholePercent, isDowngrade, payOverdueLink } from "@/shared/lib/credit";
import { queryKeys } from "@/shared/lib/queryKeys";
import { displayDayMonth, displayMoney, displayMonthName } from "@/shared/lib/utils/display";

/**
 * Dono único dos avisos de crédito em tempo real: cada evento renova a tela de crédito
 * e a carteira (o ponto vermelho do menu vem dela) e avisa do que aconteceu.
 */
export function CreditNotifications() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const renew = () => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.credit() });
    void queryClient.invalidateQueries({ queryKey: queryKeys.portfolio() });
  };

  useRealtime("credit_installment_paid", (event) => {
    renew();
    toast.success("Parcela paga", {
      description: `Empréstimo ${event.loan_number} · ${displayMoney(event.amount)} · ${event.installment_number} de ${event.total_installments}`,
    });
  });

  useRealtime("credit_monthly_summary", (event) => {
    renew();
    toast.success(`Parcelas de ${displayMonthName(event.month)} pagas`, {
      description: `${event.installments} ${event.installments === 1 ? "parcela" : "parcelas"} · ${displayMoney(event.amount)}`,
    });
  });

  useRealtime("credit_installment_late", (event) => {
    renew();
    toast.error("Parcela em atraso", {
      icon: <TriangleAlert className="size-4 text-toast-error" />,
      description: `Faltou caixa para os ${displayMoney(event.amount)} do Empréstimo ${event.loan_number}. Multa de 2% e mora correndo.`,
      action: { label: "Pagar", onClick: () => void navigate(payOverdueLink(event.loan_id)) },
    });
  });

  useRealtime("credit_installment_warning", (event) => {
    renew();
    toast.warning(`O caixa não cobre a parcela de ${displayDayMonth(event.due_date)}`, {
      icon: <Clock className="size-4 text-toast-warning" />,
      description: `Faltam ${displayMoney(event.shortfall)} para os ${displayMoney(event.amount)}. Venda algo ou ela atrasa.`,
      action: { label: "Ver", onClick: () => void navigate("/credit") },
    });
  });

  useRealtime("credit_rating_changed", (event) => {
    renew();
    const description =
      event.spread === null
        ? "Sem crédito novo nesta nota."
        : `Próximos empréstimos a ${displaySelicSpread(event.spread)}, limite de ${displayWholePercent(event.debt_limit)}.`;
    const upgraded = event.after !== "D" && !isDowngrade(event.before, event.after);
    const show = event.after === "D" ? toast.error : upgraded ? toast.success : toast.warning;
    // A subida de nota leva a seta de alta; rebaixamento e nota D ficam com o ícone do tipo
    show(`Nota de risco: ${event.before} → ${event.after}`, {
      description,
      icon: upgraded ? <TrendingUp className="size-4 text-toast-success" /> : undefined,
    });
  });

  useRealtime("credit_loan_paid_off", (event) => {
    renew();
    const saved = Number(event.interest_saved);
    toast.success(`Empréstimo ${event.loan_number} quitado`, {
      description:
        saved > 0
          ? `Você pagou ${displayMoney(event.amount)} e deixou de pagar ${displayMoney(saved)} de juro.`
          : `Você pagou ${displayMoney(event.amount)}.`,
    });
  });

  return null;
}
