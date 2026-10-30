import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { useAuth } from "@/shared/hooks/useAuth";
import { useNotificationPreferences } from "@/shared/hooks/useNotificationPreferences";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { ElectionPanel, ElectionRound, GovernmentPanel } from "@/types";
import { campaignToast, toastEffect } from "../lib/campaign";
import { dealAnsweredToast, dealBrokenToast, dealEndedToast } from "../lib/deal-toast";
import { impeachmentToast, measureVotedToast, monthClosedToast } from "../lib/measure-toast";
import { endorsementToast, roundResultToast } from "../lib/runoff-toast";
import { campaignQuery } from "../hooks/queries/useCampaign";
import { useRenewElection } from "../hooks/mutations/useRenewElection";
import { useRenewBase } from "../hooks/mutations/useRenewBase";
import { useDealDialog } from "../hooks/useDealDialog";
import { DealProposalDialog } from "./deal-proposal-dialog";
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
  const renewBase = useRenewBase();
  const dealDialog = useDealDialog();

  const openGovernment = () => void navigate("/government");
  const openCampaign = () => void navigate("/election", { state: { tab: "campaign" } });

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
          const notice = roundResultToast(panel, last);
          toast[notice.tone](notice.title, { description: notice.description });
        });
        break;
      case "ENDORSEMENT": {
        const notice = endorsementToast(event);
        toast[notice.tone](notice.title, { description: notice.description });
        break;
      }
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
        if (notice && mine) {
          // O efeito vem da linha do histórico do próprio partido: o aviso público não carrega o dado
          void queryClient
            .query({ ...campaignQuery(), staleTime: 0 })
            .then((campaign) =>
              campaign.recent.find((entry) =>
                event.rival_abbr === mine.abbr
                  ? entry.kind === "ATTACK_RECEIVED" && entry.party_abbr === event.party_abbr
                  : entry.nickname === event.actor && entry.kind === event.campaign_action,
              ),
            )
            .catch(() => undefined)
            .then((entry) => {
              toast[notice.tone](notice.title, {
                description: entry ? toastEffect(entry, mine.abbr) : notice.description,
                action: { label: "Ver", onClick: openCampaign },
              });
            });
        }
        break;
      }
      case "DEAL_PROPOSED":
        // A proposta ao partido de jogador abre na tela do líder, em qualquer página
        if (event.target === me) dealDialog.setOpen(true);
        break;
      case "DEAL_ANSWERED":
        if (event.target === me) {
          const notice = dealAnsweredToast(event);
          toast[notice.tone](notice.title, { description: notice.description });
        }
        break;
      case "DEAL_BROKEN":
        // Avisa o lado que sofreu a quebra; quem rompeu já viu o diálogo
        if (event.target === me) {
          const notice = dealBrokenToast(event);
          toast[notice.tone](notice.title, { description: notice.description });
        }
        break;
      case "DEAL_ENDED": {
        // O fim do acordo é aviso de quem governa
        const panel = queryClient.getQueryData<GovernmentPanel>(queryKeys.government());
        if (panel?.is_president) {
          const notice = dealEndedToast(event);
          toast[notice.tone](notice.title, { description: notice.description });
        }
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
      case "UPDATED":
        break;
    }
    renew();
    if (event.kind.startsWith("DEAL_")) renewBase();
  });

  return (
    <>
      <DealProposalDialog open={dealDialog.open} onOpenChange={dealDialog.setOpen} />
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
