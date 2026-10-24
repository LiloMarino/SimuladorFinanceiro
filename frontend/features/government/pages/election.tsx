import { useState } from "react";
import { MailQuestion, UserPlus, HandCoins } from "lucide-react";
import { Alert, AlertAction, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import usePageLabel from "@/shared/hooks/usePageLabel";
import { usePortfolio } from "@/shared/hooks/queries/usePortfolio";
import { useAuth } from "@/shared/hooks/useAuth";
import { displayDayMonth } from "@/shared/lib/utils/display";
import type { ElectionPanel } from "@/types";
import { ContributionDialog } from "../components/contribution-dialog";
import { DonateDialog } from "../components/donate-dialog";
import { ElectionHeader } from "../components/election-header";
import { BeforeCampaignEmpty, ElectionError, ElectionSkeleton } from "../components/election-states";
import { ExpelDialog } from "../components/expel-dialog";
import { FoundPartyDialog } from "../components/found-party-dialog";
import { JoinPartyDialog } from "../components/join-party-dialog";
import { LeavePartyDialog } from "../components/leave-party-dialog";
import { MyPartyCard } from "../components/my-party-card";
import { PartiesCard } from "../components/parties-card";
import { PollCard } from "../components/poll-card";
import { RankingCard } from "../components/ranking-card";
import { TermCard } from "../components/term-card";
import { TicketDialog } from "../components/ticket-dialog";
import { ViceInviteDialog } from "../components/vice-invite-dialog";
import { useElection } from "@/shared/hooks/queries/useElection";

export default function ElectionPage() {
  usePageLabel("Eleição");
  const { data: panel, error, refetch } = useElection();

  if (!panel) {
    return error ? <ElectionError onRetry={() => void refetch()} /> : <ElectionSkeleton />;
  }

  return <ElectionContent panel={panel} />;
}

type Dialog = "found" | "join" | "contribution" | "ticket" | "vice" | "leave" | "donate";

function ElectionContent({ panel }: { panel: ElectionPanel }) {
  const { user } = useAuth();
  const { data: portfolio } = usePortfolio();
  const [dialog, setDialog] = useState<Dialog | null>(null);
  const [joinPartyId, setJoinPartyId] = useState<number | undefined>();
  const [expelling, setExpelling] = useState<string | null>(null);

  const cash = portfolio?.cash;
  const nickname = user?.nickname ?? "";
  const mine = panel.my_party;
  const party = mine ? panel.parties.find((candidate) => candidate.id === mine.party_id) : undefined;
  const playerParties = panel.parties.filter((candidate) => !candidate.is_computer);
  const takenColors = panel.parties.map((candidate) => candidate.color).filter((color): color is string => !!color);
  const campaignOpen = panel.phase !== "BEFORE_CAMPAIGN";
  const hasTerm = panel.term !== null || panel.pending_term !== null;

  const close = (open: boolean) => !open && setDialog(null);
  const openJoin = (partyId?: number) => {
    setJoinPartyId(partyId);
    setDialog("join");
  };

  // Vaga de vice aberta: a chapa tem candidato e ainda não tem vice nem convite pendente
  const viceOpen =
    !!party && !!mine?.is_founder && panel.can_edit_ticket && party.vice === null && party.vice_phase === "NONE";

  return (
    <div className="grid gap-5">
      <ElectionHeader panel={panel} onJoin={() => openJoin()} onFound={() => setDialog("found")} />

      {mine?.vice === "PENDING" && party && (
        <Alert variant="info">
          <MailQuestion />
          <AlertTitle>{party.founder ?? party.name} convidou você para vice no {party.abbr}</AlertTitle>
          <AlertDescription>
            Aceite ou recuse até {displayDayMonth(panel.dates.ticket_deadline)}; sem resposta, a chapa concorre sem vice.
          </AlertDescription>
          <AlertAction>
            <Button size="sm" onClick={() => setDialog("vice")}>
              Responder
            </Button>
          </AlertAction>
        </Alert>
      )}

      {viceOpen && (
        <Alert variant="warning">
          <UserPlus />
          <AlertTitle>A chapa do {party.abbr} está sem vice</AlertTitle>
          <AlertDescription>
            Indique um filiado até {displayDayMonth(panel.dates.ticket_deadline)}; ele precisa aceitar o convite.
          </AlertDescription>
          <AlertAction>
            <Button size="sm" variant="outline" onClick={() => setDialog("ticket")}>
              Indicar vice
            </Button>
          </AlertAction>
        </Alert>
      )}

      {panel.can_donate && (
        <Alert variant="info">
          <HandCoins />
          <AlertTitle>Entre os turnos, os filiados podem doar a um finalista</AlertTitle>
          <AlertDescription>
            Até {displayDayMonth(panel.dates.donation_deadline)}. A doação é pública e sai do seu patrimônio.
          </AlertDescription>
          <AlertAction>
            <Button size="sm" onClick={() => setDialog("donate")}>
              Doar
            </Button>
          </AlertAction>
        </Alert>
      )}

      {!campaignOpen && !hasTerm && <BeforeCampaignEmpty panel={panel} />}

      {(campaignOpen || hasTerm) && (
        <div className="grid items-start gap-5 xl:grid-cols-[minmax(0,1fr)_380px]">
          <div className="grid min-w-0 gap-5">
            {campaignOpen && <PollCard panel={panel} />}
            {campaignOpen && <PartiesCard panel={panel} />}
            <RankingCard panel={panel} />
          </div>
          <div className="grid gap-5">
            {party && mine && (
              <MyPartyCard
                panel={panel}
                party={party}
                nickname={nickname}
                onEditTicket={() => setDialog("ticket")}
                onChangeContribution={() => setDialog("contribution")}
                onExpel={setExpelling}
                onLeave={() => setDialog("leave")}
              />
            )}
            <TermCard panel={panel} />
          </div>
        </div>
      )}

      {/* Diálogos */}
      <FoundPartyDialog
        open={dialog === "found"}
        onOpenChange={close}
        takenColors={takenColors}
        cash={cash}
      />
      <JoinPartyDialog
        open={dialog === "join"}
        onOpenChange={close}
        parties={playerParties}
        initialPartyId={joinPartyId}
        cash={cash}
      />
      {party && mine && (
        <>
          <ContributionDialog
            open={dialog === "contribution"}
            onOpenChange={close}
            party={party}
            current={String(mine.contribution)}
            cash={cash}
          />
          <TicketDialog open={dialog === "ticket"} onOpenChange={close} party={party} panel={panel} cash={cash} />
          <ViceInviteDialog open={dialog === "vice"} onOpenChange={close} party={party} panel={panel} />
          <LeavePartyDialog
            open={dialog === "leave"}
            onOpenChange={close}
            party={party}
            isFounder={mine.is_founder}
            isVice={mine.vice === "ACCEPTED"}
          />
          <ExpelDialog nickname={expelling} onClose={() => setExpelling(null)} party={party} />
        </>
      )}
      <DonateDialog open={dialog === "donate"} onOpenChange={close} panel={panel} cash={cash} />
    </div>
  );
}
