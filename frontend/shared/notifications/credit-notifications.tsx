import { useQueryClient } from "@tanstack/react-query";
import { TrendingUp } from "lucide-react";
import { toast } from "sonner";
import { useNotificationPreferences } from "@/shared/hooks/useNotificationPreferences";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { displaySelicSpread, displayWholePercent, isDowngrade } from "@/shared/lib/credit";
import { queryKeys } from "@/shared/lib/queryKeys";
import { displayMoney, displayMonthName } from "@/shared/lib/utils/display";

/**
 * Dono único dos avisos de crédito em tempo real: cada evento renova a tela de crédito
 * e a carteira (o ponto vermelho do menu vem dela) e avisa do que aconteceu.
 */
export function CreditNotifications() {
  const queryClient = useQueryClient();
  const { isToastOn } = useNotificationPreferences();

  const renew = () => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.credit() });
    void queryClient.invalidateQueries({ queryKey: queryKeys.portfolio() });
  };

  useRealtime("credit_installment_paid", (event) => {
    renew();
    if (!isToastOn("CREDIT_PAYMENTS")) return;
    toast.success("Parcela paga", {
      description: `Empréstimo ${event.loan_number} · ${displayMoney(event.amount)} · ${event.installment_number} de ${event.total_installments}`,
    });
  });

  useRealtime("credit_monthly_summary", (event) => {
    renew();
    if (!isToastOn("CREDIT_PAYMENTS")) return;
    toast.success(`Parcelas de ${displayMonthName(event.month)} pagas`, {
      description: `${event.installments} ${event.installments === 1 ? "parcela" : "parcelas"} · ${displayMoney(event.amount)}`,
    });
  });

  // Atraso e parcela sem caixa são pendências: o aviso nasce na lista de pendências; aqui só renovam a tela
  useRealtime("credit_installment_late", renew);
  useRealtime("credit_installment_warning", renew);

  useRealtime("credit_rating_changed", (event) => {
    renew();
    if (!isToastOn("CREDIT_RATING")) return;
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
    if (!isToastOn("CREDIT_PAYMENTS")) return;
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
