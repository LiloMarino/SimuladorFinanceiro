import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { useAuth } from "@/shared/hooks/useAuth";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { queryKeys } from "@/shared/lib/queryKeys";
import { displayMoney } from "@/shared/lib/utils/display";
import type { ElectionPanel, ElectionRound, GovernmentPanel, PortfolioState } from "@/types";
import { inForceToast, votedToast, warningToast } from "../lib/measure-toast";
import { donationContext, roundToast } from "../lib/round-toast";
import { ImpeachmentDialog } from "./impeachment-dialog";
import { RoundResultDialog } from "./round-result-dialog";

/**
 * Dono único dos avisos da eleição em tempo real: cada evento renova a página da eleição
 * e a carteira (contribuição e doação saem do caixa) e conta o que aconteceu.
 * O resultado de um turno e o impeachment abrem um diálogo para todos, ao vivo, com a partida pausada.
 */
export function GovernmentNotifications() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { user } = useAuth();
  // O painel viaja com o turno: o diálogo mostra as datas e a doação do momento da apuração
  const [shown, setShown] = useState<{ result: ElectionRound; panel: ElectionPanel } | null>(null);
  const [impeachment, setImpeachment] = useState<GovernmentPanel | null>(null);
  const me = user?.nickname;

  const renew = () => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.election() });
    void queryClient.invalidateQueries({ queryKey: queryKeys.government() });
    void queryClient.invalidateQueries({ queryKey: queryKeys.portfolio() });
  };

  const openGovernment = () => void navigate("/government");
  const showMeasure = (notice: {
    tone: "success" | "info" | "warning" | "error";
    title: string;
    description: string;
  }) =>
    toast[notice.tone](notice.title, {
      description: notice.description,
      action: { label: "Ver medidas", onClick: openGovernment },
    });

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
        toast.info(`${event.actor} doou ${displayMoney(event.amount ?? 0)} ao ${abbr}`, {
          description:
            donationContext(queryClient.getQueryData<ElectionPanel>(queryKeys.election()), abbr) ?? undefined,
        });
        break;
      case "ELECTION_RESULT":
        // O resultado só chega depois de o painel atualizar: o diálogo lê o turno apurado do cache
        void queryClient.refetchQueries({ queryKey: queryKeys.election() }).then(() => {
          const panel = queryClient.getQueryData<ElectionPanel>(queryKeys.election());
          const last = panel?.last_result;
          if (!panel || !last || last.round !== event.round) return;
          setShown({ result: last, panel });
          const notice = roundToast(panel);
          if (notice) {
            toast[notice.tone](notice.title, {
              description: notice.description,
              action: notice.donate
                ? { label: "Doar a um finalista", onClick: () => void navigate("/election") }
                : undefined,
            });
          }
        });
        break;
      case "TERM_STARTED":
        toast.success(`${event.winner_name ?? `O candidato do ${event.winner_abbr ?? "partido eleito"}`} toma posse`, {
          description: "O mandato dura 4 anos, com uma reeleição possível.",
          action: { label: "Ver", onClick: openGovernment },
        });
        break;
      case "MEASURE_PROPOSED":
        toast.info(`${event.actor} propôs: ${event.measure_title}`, {
          action: { label: "Ver fila", onClick: openGovernment },
        });
        break;
      case "MEASURE_WITHDRAWN":
        toast.info(`${event.actor} retirou: ${event.measure_title}`);
        break;
      case "MEASURE_VOTED": {
        const portfolio = queryClient.getQueryData<PortfolioState>(queryKeys.portfolio());
        showMeasure(votedToast(event, portfolio?.variable_income.map((position) => position.ticker) ?? []));
        break;
      }
      case "MEASURE_IN_FORCE":
        showMeasure(inForceToast(event));
        break;
      case "IMPEACHMENT_WARNING":
        if (event.actor === me) {
          const floor = queryClient.getQueryData<GovernmentPanel>(queryKeys.government())?.approval?.floor ?? 25;
          const notice = warningToast(event, floor);
          toast.error(notice.title, {
            description: notice.description,
            action: { label: "Ver governo", onClick: openGovernment },
          });
        }
        break;
      case "IMPEACHMENT":
        // O diálogo lê o governo já com o sucessor no cache
        void queryClient.refetchQueries({ queryKey: queryKeys.government() }).then(() => {
          setImpeachment(queryClient.getQueryData<GovernmentPanel>(queryKeys.government()) ?? null);
        });
        break;
      case "UPDATED":
        break;
    }
    renew();
  });

  return (
    <>
      <ImpeachmentDialog panel={impeachment} onClose={() => setImpeachment(null)} />
      <RoundResultDialog
        result={shown?.result ?? null}
        panel={shown?.panel}
        onClose={() => setShown(null)}
        onOpenPage={() => {
          setShown(null);
          void navigate("/election");
        }}
      />
    </>
  );
}
