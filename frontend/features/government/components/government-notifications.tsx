import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { useAuth } from "@/shared/hooks/useAuth";
import { useNotificationPreferences } from "@/shared/hooks/useNotificationPreferences";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { ElectionPanel, ElectionRound, GovernmentPanel } from "@/types";
import { campaignToast } from "../lib/campaign";
import { impeachmentToast, measureVotedToast, monthClosedToast } from "../lib/measure-toast";
import { useRenewElection } from "../hooks/mutations/useRenewElection";
import { ImpeachmentDialog } from "./impeachment-dialog";
import { RoundResultDialog } from "./round-result-dialog";

// Votos Sim para a casa tirar o presidente
const IMPEACHMENT_VOTES = 68;

/**
 * Dono único dos avisos da eleição em tempo real: cada evento renova a página da eleição
 * e a carteira (contribuição e doação saem do caixa) e conta o que aconteceu.
 * O resultado de um turno e o impeachment abrem um diálogo para todos, ao vivo, com a partida pausada.
 * A abertura da campanha e o convite de vice são pendências: o diálogo abre pela lista.
 */
export function GovernmentNotifications() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { isToastOn } = useNotificationPreferences();
  // O painel viaja com o turno: o diálogo mostra as datas e a doação do momento da apuração
  const [shown, setShown] = useState<{ result: ElectionRound; panel: ElectionPanel } | null>(null);
  const [impeachment, setImpeachment] = useState<GovernmentPanel | null>(null);
  const me = user?.nickname;

  const renew = useRenewElection();

  const openGovernment = () => void navigate("/government");

  useRealtime("government_update", (event) => {
    const abbr = event.party_abbr ?? "";

    switch (event.kind) {
      case "VICE_ANSWERED":
        if (event.target === me && isToastOn("VICE_ANSWER")) {
          toast[event.accepted ? "success" : "warning"](
            `${event.actor} ${event.accepted ? "aceitou" : "recusou"} ser seu vice no ${abbr}`,
          );
        }
        break;
      case "EXPELLED":
        if (event.target === me) {
          toast.error(`Você foi expulso do ${abbr}`, {
            description: "A contribuição parou. Dá para se filiar a outro partido ou fundar o seu.",
          });
        }
        break;
      case "ELECTION_RESULT":
        // O resultado só chega depois de o painel atualizar: o diálogo lê o turno apurado do cache
        void queryClient.refetchQueries({ queryKey: queryKeys.election() }).then(() => {
          const panel = queryClient.getQueryData<ElectionPanel>(queryKeys.election());
          const last = panel?.last_result;
          if (!panel || !last || last.round !== event.round) return;
          setShown({ result: last, panel });
        });
        break;
      case "MONTH_CLOSED": {
        // O fechamento conta o que mudou no apoio só aos filiados do partido do governo
        const election = queryClient.getQueryData<ElectionPanel>(queryKeys.election());
        const mine = election?.parties.find((party) => party.id === election.my_party?.party_id);
        if (mine && mine.abbr === event.party_abbr) {
          const notice = monthClosedToast(event);
          toast[notice.tone](notice.title, {
            description: notice.description,
            action: { label: "Abrir o Governo", onClick: openGovernment },
          });
        }
        break;
      }
      case "IMPEACHMENT":
        // O diálogo lê o governo já com o sucessor no cache
        void queryClient.refetchQueries({ queryKey: queryKeys.government() }).then(() => {
          setImpeachment(queryClient.getQueryData<GovernmentPanel>(queryKeys.government()) ?? null);
        });
        break;
      case "MEASURE_VOTED": {
        const notice = measureVotedToast(event);
        toast[notice.tone](notice.title, { description: notice.description });
        break;
      }
      case "IMPEACHMENT_REQUESTED":
      case "IMPEACHMENT_VOTED": {
        // O pedido aprovado vira o diálogo do impeachment; aqui só o aberto e o rejeitado
        if (event.kind === "IMPEACHMENT_VOTED" && event.accepted) break;
        const notice = impeachmentToast(event, IMPEACHMENT_VOTES);
        toast[notice.tone](notice.title, { description: notice.description });
        break;
      }
      case "CAMPAIGN_ACTION": {
        // Quem fez a ação já viu o dado no diálogo; os outros filiados e o partido atacado recebem o aviso
        const election = queryClient.getQueryData<ElectionPanel>(queryKeys.election());
        const mine = election?.parties.find((party) => party.id === election.my_party?.party_id);
        const notice = campaignToast(event, mine && me ? { abbr: mine.abbr, nickname: me } : undefined);
        if (notice) toast[notice.tone](notice.title, { description: notice.description });
        break;
      }
      // O jornal da partida conta estes fatos (news_published) e as pendências, os que pedem ação; aqui só renovam a tela
      case "CAMPAIGN_OPENED":
      case "VICE_INVITED":
      case "IMPEACHMENT_WARNING":
      case "TICKETS_CLOSING":
      case "ELECTION_EVE":
      case "PARTY_FOUNDED":
      case "DONATION":
      case "TERM_STARTED":
      case "MEASURE_PROPOSED":
      case "MEASURE_WITHDRAWN":
      case "MEASURE_IN_FORCE":
      case "HOUSE_ELECTED":
      case "PROMISES_SET":
      case "PROMISES_SETTLED":
      case "ENDORSEMENT":
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
