import { useNavigate } from "react-router-dom";
import { Users } from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { useNotificationPreferences } from "@/shared/hooks/useNotificationPreferences";
import { queryKeys } from "../lib/queryKeys";
import { displayMoney, displayQuantity } from "../lib/utils/display";
import { AchievementToast } from "./achievement-toast";

const ACHIEVEMENT_TOAST_MS = 6000;

/** Avisos do que acontece longe da tela atual, com atalho para ver. */
export function GlobalNotifications() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { preferences } = useNotificationPreferences();

  useRealtime(
    "order_executed",
    (event) => {
      // Cada execução é um aviso; o Toaster os empilha com o mais novo na frente
      toast.success(`${event.action === "buy" ? "Compra" : "Venda"} executada`, {
        description: `${displayQuantity(event.quantity)} ${event.ticker} a ${displayMoney(event.price)}`,
        action: { label: "Ver", onClick: () => void navigate(`/variable-income/${event.ticker}`) },
      });
    },
    preferences.orders.executed,
  );

  useRealtime(
    "order_partial_executed",
    (event) => {
      const missing = event.action === "sell" ? "comprador" : "vendedor";
      toast.warning(`${event.action === "buy" ? "Compra" : "Venda"} executada em parte`, {
        description: `${displayQuantity(event.quantity)} ${event.ticker} executadas, ${displayQuantity(event.remaining)} seguem abertas · faltou ${missing}`,
        action: { label: "Ver ordem", onClick: () => void navigate(`/variable-income/${event.ticker}`) },
      });
    },
    preferences.orders.partial,
  );

  useRealtime(
    "player_join",
    ({ nickname }) => {
      toast.info(`${nickname} entrou na sala`, { icon: <Users className="size-4 text-toast-info" /> });
    },
    preferences.players.join_exit,
  );

  useRealtime(
    "player_exit",
    ({ nickname }) => {
      toast.info(`${nickname} saiu da sala`);
    },
    preferences.players.join_exit,
  );

  // Conquista nova: o aviso (o sonner pausa a contagem com o mouse em cima) e a lista renovada
  useRealtime("achievement_unlocked", ({ achievements }) => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.achievements() });
    toast.custom(
      (id) => (
        <AchievementToast
          achievements={achievements}
          onSeeAll={() => {
            toast.dismiss(id);
            void navigate("/achievements");
          }}
        />
      ),
      { duration: ACHIEVEMENT_TOAST_MS },
    );
  });

  return null;
}
