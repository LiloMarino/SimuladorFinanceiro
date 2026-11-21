import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { useAuth } from "@/shared/hooks/useAuth";
import { useNotificationPreferences } from "@/shared/hooks/useNotificationPreferences";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { GovernmentNotice } from "@/types";
import { campaignToast } from "../lib/campaign";
import { dealAnsweredToast, dealBrokenToast, dealEndedToast, dealLeftToast } from "../lib/deal-toast";
import { federationAnsweredToast, federationLeftToast, federationProposedToast } from "../lib/federation-toast";
import { impeachmentToast, measureVotedToast, monthClosedToast } from "../lib/measure-toast";
import { endorsementToast, roundResultToast } from "../lib/runoff-toast";
import { useDealDialog } from "../hooks/useDealDialog";
import { DealProposalDialog } from "./deal-proposal-dialog";
import { ImpeachmentDialog } from "./impeachment-dialog";

// Votos Sim para a casa tirar o presidente
const IMPEACHMENT_VOTES = 68;

/**
 * Dono único dos avisos da eleição em tempo real: cada evento conta o que aconteceu com o dado
 * que o próprio aviso carrega. Os painéis chegam pelos seus eventos, e o servidor entrega cada
 * aviso a quem ele interessa.
 * O impeachment abre um diálogo para todos, ao vivo, com a partida pausada; o do resultado de um turno é o `PausedRoundResult`.
 * A abertura da campanha e o convite de vice são pendências: o diálogo abre pela lista.
 */
export function GovernmentNotifications() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { isToastOn } = useNotificationPreferences();
  const [impeachment, setImpeachment] = useState<GovernmentNotice | null>(null);
  const me = user?.nickname;

  const dealDialog = useDealDialog();

  const openGovernment = () => void navigate("/government");
  const openBase = () => void navigate("/government?tab=accounts");
  const openElection = () => void navigate("/election");
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
      case "VICE_TAKEN":
        if (event.target === me) {
          toast.warning(`${event.actor} aceitou ser vice de outra chapa`, {
            description: `O convite do ${abbr} foi recusado automaticamente. Dá para convidar outro jogador.`,
          });
        }
        break;
      case "VICE_WITHDRAWN":
        if (event.target === me) {
          toast.info(`${event.actor} retirou o convite de vice do ${abbr}`);
        }
        break;
      case "FEDERATION_TAKEN":
        if (event.target === me) {
          toast.warning(`O ${abbr} fechou federação com outro partido`, {
            description: `A proposta entre o ${abbr} e o ${event.partner_abbr ?? "seu partido"} caiu.`,
            action: { label: "Ver", onClick: openElection },
          });
        }
        break;
      case "EXPELLED":
        if (event.target === me) {
          toast.error(`Você foi expulso do ${abbr}`, {
            description: "A contribuição parou. Dá para se filiar a outro partido ou fundar o seu.",
          });
        }
        break;
      case "ELECTION_RESULT": {
        const notice = roundResultToast(event);
        toast[notice.tone](notice.title, { description: notice.description });
        break;
      }
      case "ENDORSEMENT": {
        const notice = endorsementToast(event);
        toast[notice.tone](notice.title, { description: notice.description });
        break;
      }
      case "MONTH_CLOSED": {
        // O fechamento chega só aos filiados do partido do governo
        const notice = monthClosedToast(event);
        toast[notice.tone](notice.title, {
          description: notice.description,
          action: { label: "Abrir o Governo", onClick: openGovernment },
        });
        break;
      }
      case "IMPEACHMENT":
        setImpeachment(event);
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
        // O servidor entrega a ação aos outros filiados do partido e o ataque ao partido atacado
        const notice = campaignToast(event);
        if (notice) {
          toast[notice.tone](notice.title, {
            description: notice.description,
            action: { label: "Ver", onClick: openCampaign },
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
          toast[notice.tone](notice.title, {
            description: notice.description,
            action: { label: "Ver", onClick: openBase },
          });
        }
        break;
      case "DEAL_BROKEN":
        // Avisa o lado que sofreu a quebra; quem rompeu já viu o diálogo
        if (event.target === me) {
          const notice = dealBrokenToast(event);
          toast[notice.tone](notice.title, {
            description: notice.description,
            action: { label: "Ver", onClick: openBase },
          });
        }
        break;
      case "DEAL_LEFT":
        // Quem governa recebe o aviso da bancada que saiu por falta de pagamento da cobrança
        if (event.target === me) {
          const notice = dealLeftToast(event);
          toast[notice.tone](notice.title, {
            description: notice.description,
            action: { label: "Ver", onClick: openBase },
          });
        }
        break;
      case "DEAL_ENDED": {
        // O fim do acordo chega só a quem governa
        const notice = dealEndedToast(event);
        toast[notice.tone](notice.title, {
          description: notice.description,
          action: { label: "Ver", onClick: openBase },
        });
        break;
      }
      case "FEDERATION_PROPOSED":
        // A proposta chega ao fundador do partido convidado; a resposta abre o diálogo da Eleição
        if (event.target === me) {
          const notice = federationProposedToast(event);
          toast[notice.tone](notice.title, {
            description: notice.description,
            action: {
              label: "Responder",
              onClick: () => void navigate("/election", { state: { dialog: "federation-answer" } }),
            },
          });
        }
        break;
      case "FEDERATION_ANSWERED":
        if (event.target === me) {
          const notice = federationAnsweredToast(event);
          toast[notice.tone](notice.title, {
            description: notice.description,
            action: { label: "Ver", onClick: openElection },
          });
        }
        break;
      case "FEDERATION_LEFT":
        if (event.target === me) {
          const notice = federationLeftToast(event);
          toast[notice.tone](notice.title, {
            description: notice.description,
            action: { label: "Ver", onClick: openElection },
          });
        }
        break;
      // O jornal da partida conta estes fatos (news_published) e as pendências, os que pedem ação; os painéis chegam pelos próprios eventos
      case "POLL_PUBLISHED":
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
  });

  return (
    <>
      <DealProposalDialog open={dealDialog.open} onOpenChange={dealDialog.setOpen} />
      <ImpeachmentDialog notice={impeachment} onClose={() => setImpeachment(null)} />
    </>
  );
}
