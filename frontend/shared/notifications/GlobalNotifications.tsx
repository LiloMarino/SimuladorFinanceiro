import { useNavigate } from "react-router-dom";
import { Users } from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { useAuth } from "@/shared/hooks/useAuth";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { useNotificationPreferences } from "@/shared/hooks/useNotificationPreferences";
import { queryKeys } from "../lib/queryKeys";
import { displayMoney, displayPercent, displayQuantity } from "../lib/utils/display";
import { AchievementToast } from "./achievement-toast";

const ACHIEVEMENT_TOAST_MS = 6000;

/** Avisos do que acontece longe da tela atual, com atalho para ver. */
export function GlobalNotifications() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { isToastOn } = useNotificationPreferences();
  const { logout } = useAuth();

  useRealtime(
    "order_executed",
    (event) => {
      // Cada execução é um aviso; o Toaster os empilha com o mais novo na frente
      toast.success(`${event.action === "buy" ? "Compra" : "Venda"} executada`, {
        description: `${displayQuantity(event.quantity)} ${event.ticker} a ${displayMoney(event.price)}`,
        action: { label: "Ver", onClick: () => void navigate(`/variable-income/${event.ticker}`) },
      });
    },
    isToastOn("ORDER_EXECUTED"),
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
    isToastOn("ORDER_PARTIAL"),
  );

  // O motor cancelou o resto da ordem: o motivo vem do servidor
  useRealtime("order_canceled", (event) => {
    toast.warning(`${event.action === "buy" ? "Compra" : "Venda"} cancelada`, {
      description: `${displayQuantity(event.quantity)} ${event.ticker} · ${event.reason}`,
      action: { label: "Ver", onClick: () => void navigate(`/variable-income/${event.ticker}`) },
    });
  });

  useRealtime(
    "player_join",
    ({ nickname }) => {
      toast.info(`${nickname} entrou na sala`, { icon: <Users className="size-4 text-toast-info" /> });
    },
    isToastOn("PLAYER_PRESENCE"),
  );

  useRealtime(
    "player_exit",
    ({ nickname }) => {
      toast.info(`${nickname} saiu da sala`);
    },
    isToastOn("PLAYER_PRESENCE"),
  );

  // O host tirou este jogador da sala: o aviso conta o motivo e a sessão encerra, como no botão Sair
  useRealtime("player_removed", () => {
    toast.warning("O host te removeu da sala", { description: "Entre de novo com o seu apelido para voltar." });
    void logout();
  });

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

  // Convite, resposta, saída ou remoção na co-gestão: o aviso chega só a quem a mudança atinge
  useRealtime("comanager_update", (event) => {
    const open = { label: "Ver", onClick: () => void navigate(`/funds/${event.fund_id}`) };
    const share = event.share === null ? "" : ` com ${displayPercent(event.share, 0)} das taxas`;

    switch (event.kind) {
      case "invited":
        if (isToastOn("COMANAGER_INVITED")) {
          toast.info(`${event.nickname} convidou você para co-gerir a ${event.ticker}`, {
            description: `Você opera a carteira da gestora${share}. O convite vale por 7 dias.`,
            action: { label: "Responder", onClick: open.onClick },
          });
        }
        break;
      case "accepted":
        if (isToastOn("COMANAGER_ANSWER")) {
          toast.success(`${event.nickname} aceitou co-gerir a ${event.ticker}`, { action: open });
        }
        break;
      case "declined":
        if (isToastOn("COMANAGER_ANSWER")) {
          toast.warning(`${event.nickname} recusou co-gerir a ${event.ticker}`);
        }
        break;
      case "left":
        if (isToastOn("COMANAGER_ANSWER")) {
          toast.warning(`${event.nickname} deixou a co-gestão da ${event.ticker}`, { action: open });
        }
        break;
      case "removed":
        toast.warning(`${event.nickname} tirou você da co-gestão da ${event.ticker}`, {
          description: "O acesso à carteira da gestora acabou.",
        });
        break;
      case "directed_offered":
        if (isToastOn("COMANAGER_INVITED")) {
          toast.info(`${event.nickname} oferece cotas novas da ${event.ticker} a você`, {
            description: "A oferta vale por 7 dias.",
            action: { label: "Responder", onClick: open.onClick },
          });
        }
        break;
      case "directed_accepted":
        if (isToastOn("COMANAGER_ANSWER")) {
          toast.success(`${event.nickname} aceitou as cotas novas da ${event.ticker}`, { action: open });
        }
        break;
      case "directed_declined":
        if (isToastOn("COMANAGER_ANSWER")) {
          toast.warning(`${event.nickname} recusou as cotas novas da ${event.ticker}`);
        }
        break;
      case "directed_cancelled":
        if (isToastOn("COMANAGER_ANSWER")) {
          toast.warning(`${event.nickname} cancelou a oferta de cotas novas da ${event.ticker}`);
        }
        break;
    }
  });

  return null;
}
