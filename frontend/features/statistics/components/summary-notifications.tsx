import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { useNotificationPreferences } from "@/shared/hooks/useNotificationPreferences";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { summaryTitle } from "../lib/summary";

/** O resumo do mês e a retrospectiva do ano chegam como aviso, com o atalho para a aba Resumos das estatísticas. */
export function SummaryNotifications() {
  const navigate = useNavigate();
  const { isToastOn } = useNotificationPreferences();

  useRealtime(
    "summary_delivered",
    (summary) => {
      toast.info(summaryTitle(summary.content), {
        action: { label: "Abrir", onClick: () => void navigate("/statistics?tab=summaries") },
      });
    },
    isToastOn("MONTH_SUMMARY"),
  );

  return null;
}
