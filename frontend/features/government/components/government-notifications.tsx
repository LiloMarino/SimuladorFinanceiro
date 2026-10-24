import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { useAuth } from "@/shared/hooks/useAuth";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { queryKeys } from "@/shared/lib/queryKeys";
import { displayMoney } from "@/shared/lib/utils/display";
import type { ElectionPanel, ElectionRound } from "@/types";
import { RoundResultDialog } from "./round-result-dialog";

/**
 * Dono único dos avisos da eleição em tempo real: cada evento renova a página da eleição
 * e a carteira (contribuição e doação saem do caixa) e conta o que aconteceu.
 * O resultado de um turno abre o diálogo para todos, ao vivo, com a partida pausada.
 */
export function GovernmentNotifications() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { user } = useAuth();
  // O painel viaja com o turno: o diálogo mostra as datas e a doação do momento da apuração
  const [shown, setShown] = useState<{ result: ElectionRound; panel: ElectionPanel } | null>(null);
  const me = user?.nickname;

  const renew = () => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.election() });
    void queryClient.invalidateQueries({ queryKey: queryKeys.portfolio() });
  };

  useRealtime("government_update", (event) => {
    const abbr = event.party_abbr ?? "";

    switch (event.kind) {
      case "PARTY_FOUNDED":
        toast.info(`${event.actor} fundou o ${abbr}`);
        break;
      case "EXPELLED":
        if (event.target === me) {
          toast.error(`Você foi expulso do ${abbr}`, {
            description: "A contribuição parou. Dá para se filiar a outro partido ou fundar o seu.",
          });
        } else {
          toast.info(`${event.target} foi expulso do ${abbr}`);
        }
        break;
      case "VICE_INVITED":
        if (event.target === me) {
          toast.info(`${event.actor} convidou você para vice no ${abbr}`, {
            action: { label: "Responder", onClick: () => void navigate("/election") },
          });
        }
        break;
      case "VICE_ANSWERED":
        if (event.target === me) {
          toast[event.accepted ? "success" : "warning"](
            `${event.actor} ${event.accepted ? "aceitou" : "recusou"} ser seu vice no ${abbr}`,
          );
        }
        break;
      case "DONATION":
        toast.info(`${event.actor} doou ${displayMoney(event.amount ?? 0)} ao ${abbr}`);
        break;
      case "ELECTION_RESULT":
        // O resultado só chega depois de o painel atualizar: o diálogo lê o turno apurado do cache
        void queryClient.refetchQueries({ queryKey: queryKeys.election() }).then(() => {
          const panel = queryClient.getQueryData<ElectionPanel>(queryKeys.election());
          const last = panel?.last_result;
          if (panel && last && last.round === event.round) setShown({ result: last, panel });
        });
        break;
      case "TERM_STARTED":
        toast.success(`${event.winner_abbr} toma posse`, {
          description: "O mandato dura 4 anos, com uma reeleição possível.",
          action: { label: "Ver", onClick: () => void navigate("/election") },
        });
        break;
      case "UPDATED":
        break;
    }
    renew();
  });

  return (
    <RoundResultDialog
      result={shown?.result ?? null}
      panel={shown?.panel}
      onClose={() => setShown(null)}
      onOpenPage={() => {
        setShown(null);
        void navigate("/election");
      }}
    />
  );
}
