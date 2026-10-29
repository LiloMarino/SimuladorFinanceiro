import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { useAuth } from "@/shared/hooks/useAuth";
import { useNotificationPreferences } from "@/shared/hooks/useNotificationPreferences";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { ElectionPanel, ElectionRound, GovernmentNotice, GovernmentPanel } from "@/types";
import { campaignToast } from "../lib/campaign";
import { monthClosedToast, warningToast } from "../lib/measure-toast";
import type { ElectionShortcut } from "../lib/election";
import { useRenewElection } from "../hooks/mutations/useRenewElection";
import { CampaignOpenedDialog } from "./campaign-opened-dialog";
import { ImpeachmentDialog } from "./impeachment-dialog";
import { RoundResultDialog } from "./round-result-dialog";
import { ViceInviteDialog } from "./vice-invite-dialog";

/**
 * Dono único dos avisos da eleição em tempo real: cada evento renova a página da eleição
 * e a carteira (contribuição e doação saem do caixa) e conta o que aconteceu.
 * A abertura da campanha, o resultado de um turno e o impeachment abrem um diálogo para todos, ao vivo, com a partida pausada.
 */
export function GovernmentNotifications() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { isToastOn } = useNotificationPreferences();
  // O painel viaja com o turno: o diálogo mostra as datas e a doação do momento da apuração
  const [shown, setShown] = useState<{ result: ElectionRound; panel: ElectionPanel } | null>(null);
  const [impeachment, setImpeachment] = useState<GovernmentPanel | null>(null);
  const [campaign, setCampaign] = useState<GovernmentNotice | null>(null);
  const [viceInvite, setViceInvite] = useState(false);
  const me = user?.nickname;

  const renew = useRenewElection();

  const openGovernment = () => void navigate("/government");

  useRealtime("government_update", (event) => {
    const abbr = event.party_abbr ?? "";

    switch (event.kind) {
      case "CAMPAIGN_OPENED":
        // O diálogo lê do painel atualizado se quem vê já tem partido
        void queryClient.refetchQueries({ queryKey: queryKeys.election() }).then(() => setCampaign(event));
        break;
      case "VICE_INVITED":
        // O convite abre na tela de quem foi indicado, do partido que for, já com o painel atualizado
        if (event.target === me) {
          void queryClient.refetchQueries({ queryKey: queryKeys.election() }).then(() => setViceInvite(true));
        }
        break;
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
      case "IMPEACHMENT_WARNING":
        if (event.actor === me) {
          const approval = queryClient.getQueryData<GovernmentPanel>(queryKeys.government())?.approval;
          const notice = warningToast(event, {
            floor: approval?.floor ?? 25,
            impeachment_months: approval?.impeachment_months ?? 6,
          });
          toast.error(notice.title, {
            description: notice.description,
            action: { label: "Ver governo", onClick: openGovernment },
          });
        }
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
      case "CAMPAIGN_ACTION": {
        // Quem fez a ação já viu o dado no diálogo; os outros filiados e o partido atacado recebem o aviso
        const election = queryClient.getQueryData<ElectionPanel>(queryKeys.election());
        const mine = election?.parties.find((party) => party.id === election.my_party?.party_id);
        const notice = campaignToast(event, mine && me ? { abbr: mine.abbr, nickname: me } : undefined);
        if (notice) toast[notice.tone](notice.title, { description: notice.description });
        break;
      }
      // O jornal da partida conta estes fatos (news_published); aqui só renovam a tela
      case "TICKETS_CLOSING":
      case "ELECTION_EVE":
      case "PARTY_FOUNDED":
      case "DONATION":
      case "TERM_STARTED":
      case "MEASURE_PROPOSED":
      case "MEASURE_WITHDRAWN":
      case "MEASURE_VOTED":
      case "MEASURE_IN_FORCE":
      case "PROMISES_SET":
      case "PROMISES_SETTLED":
      case "ENDORSEMENT":
      case "UPDATED":
        break;
    }
    renew();
  });

  const openShortcut = (dialog: ElectionShortcut) => {
    setCampaign(null);
    void navigate("/election", { state: { dialog } });
  };

  const electionPanel = queryClient.getQueryData<ElectionPanel>(queryKeys.election());

  return (
    <>
      {electionPanel && <ViceInviteDialog open={viceInvite} onOpenChange={setViceInvite} panel={electionPanel} />}
      <CampaignOpenedDialog
        notice={campaign}
        panel={electionPanel}
        onClose={() => setCampaign(null)}
        onShortcut={openShortcut}
      />
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
