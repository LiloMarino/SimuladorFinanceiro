import { useState } from "react";
import { useLocation } from "react-router-dom";
import { Flag, Lock, MailQuestion, UserPlus, HandCoins } from "lucide-react";
import { Alert, AlertAction, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/shared/components/ui/tabs";
import usePageLabel from "@/shared/hooks/usePageLabel";
import { usePortfolio } from "@/shared/hooks/queries/usePortfolio";
import { useAuth } from "@/shared/hooks/useAuth";
import { displayDayMonth } from "@/shared/lib/utils/display";
import type { ElectionPanel } from "@/types";
import { CampaignSection } from "../components/campaign-section";
import { ChooseFlagsDialog } from "../components/choose-flags-dialog";
import { ContributionDialog } from "../components/contribution-dialog";
import { DonateDialog } from "../components/donate-dialog";
import { ElectionHeader } from "../components/election-header";
import { ElectorateCard } from "../components/electorate-card";
import { BeforeCampaignEmpty, ElectionError, ElectionSkeleton } from "../components/election-states";
import { ExpelDialog } from "../components/expel-dialog";
import { FoundPartyDialog } from "../components/found-party-dialog";
import { JoinPartyDialog } from "../components/join-party-dialog";
import { LeavePartyDialog } from "../components/leave-party-dialog";
import { MyPartyCard } from "../components/my-party-card";
import { PartiesCard } from "../components/parties-card";
import { PartyProfilesCard } from "../components/party-profiles-card";
import { PollCard } from "../components/poll-card";
import { PromisesDialog } from "../components/promises-dialog";
import { RankingCard } from "../components/ranking-card";
import { TermCard } from "../components/term-card";
import { TicketDialog } from "../components/ticket-dialog";
import { ViceInviteDialog } from "../components/vice-invite-dialog";
import type { ElectionShortcut } from "../lib/election";
import { useElection } from "@/shared/hooks/queries/useElection";

export default function ElectionPage() {
  usePageLabel("Eleição");
  const { data: panel, error, refetch } = useElection();
  const location = useLocation();
  const shortcut = (location.state as { dialog?: ElectionShortcut } | null)?.dialog;

  if (!panel) {
    return error ? <ElectionError onRetry={() => void refetch()} /> : <ElectionSkeleton />;
  }

  // Cada navegação remonta a página, e o atalho de quem chegou pelo aviso da campanha abre o diálogo
  return <ElectionContent key={location.key} panel={panel} initialDialog={shortcut ?? null} />;
}

type Dialog = "found" | "join" | "contribution" | "ticket" | "promises" | "vice" | "leave" | "donate" | "flags";
type Tab = "race" | "campaign";

function ElectionContent({ panel, initialDialog }: { panel: ElectionPanel; initialDialog: Dialog | null }) {
  const { user } = useAuth();
  const { data: portfolio } = usePortfolio();
  const [dialog, setDialog] = useState<Dialog | null>(initialDialog);
  const [joinPartyId, setJoinPartyId] = useState<number | undefined>();
  const [expelling, setExpelling] = useState<string | null>(null);
  const [tab, setTab] = useState<Tab>("race");

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

  // A chapa que convidou quem vê para vice, do partido dele ou de outro
  const invitingParty = panel.parties.find((candidate) => candidate.id === panel.my_vice?.party_id);

  // Vaga de vice aberta: a chapa tem candidato e ainda não tem vice nem convite pendente
  const viceOpen =
    !!party && !!mine?.is_founder && panel.can_edit_ticket && party.vice === null && party.vice_phase === "NONE";

  // A corrida é pública: quem não é filiado vê só ela, sem a barra de abas
  const race = (
    <div className="grid gap-5">
      {campaignOpen && <PollCard panel={panel} />}
      <div className="grid items-start gap-5 xl:grid-cols-[minmax(0,1fr)_380px]">
        <div className="grid min-w-0 gap-5">
          {panel.parties.length > 0 && <PartyProfilesCard panel={panel} />}
          {campaignOpen && <PartiesCard panel={panel} />}
        </div>
        <div className="grid gap-5">
          <TermCard panel={panel} />
          <RankingCard panel={panel} />
        </div>
      </div>
    </div>
  );

  return (
    <div className="grid gap-5">
      <ElectionHeader panel={panel} onJoin={() => openJoin()} onFound={() => setDialog("found")} />

      {panel.my_vice?.phase === "PENDING" && invitingParty && (
        <Alert variant="info">
          <MailQuestion />
          <AlertTitle>
            {invitingParty.founder ?? invitingParty.name} convidou você para vice no {invitingParty.abbr}
          </AlertTitle>
          <AlertDescription>
            Aceite ou recuse até {displayDayMonth(panel.dates.ticket_deadline)}; sem resposta, a chapa concorre sem
            vice.
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
            Indique um jogador da sala até {displayDayMonth(panel.dates.ticket_deadline)}; ele precisa aceitar o
            convite.
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

      {party && party.flags === null && (
        <Alert variant={mine?.is_founder ? "warning" : "info"}>
          {mine?.is_founder ? <Flag /> : <Lock />}
          <AlertTitle>
            {mine?.is_founder
              ? `Escolha as bandeiras do ${party.abbr}`
              : `O fundador do ${party.abbr} ainda não escolheu as bandeiras`}
          </AlertTitle>
          <AlertDescription>
            {mine?.is_founder
              ? `Até você escolher 3 bandeiras, o ${party.abbr} entra na pesquisa com um perfil neutro, com a mesma afinidade em todos os grupos.`
              : "Até a escolha, o partido entra na pesquisa com um perfil neutro, com a mesma afinidade em todos os grupos."}
          </AlertDescription>
          {mine?.is_founder && (
            <AlertAction>
              <Button size="sm" onClick={() => setDialog("flags")}>
                Escolher bandeiras
              </Button>
            </AlertAction>
          )}
        </Alert>
      )}

      {!campaignOpen && !hasTerm && <BeforeCampaignEmpty panel={panel} />}

      {(campaignOpen || hasTerm) &&
        (party && mine ? (
          <Tabs value={tab} onValueChange={(value) => setTab(value as Tab)}>
            <TabsList variant="line">
              <TabsTrigger value="race">Corrida</TabsTrigger>
              <TabsTrigger value="campaign">Campanha do {party.abbr}</TabsTrigger>
            </TabsList>
            <TabsContent value="race">{race}</TabsContent>
            <TabsContent value="campaign">
              <div className="grid gap-5">
                <CampaignSection
                  panel={panel}
                  party={party}
                  cash={cash}
                  nickname={nickname}
                  onChangeContribution={() => setDialog("contribution")}
                />
                <div className="grid items-start gap-5 xl:grid-cols-[minmax(0,1fr)_380px]">
                  <div className="grid min-w-0 gap-5">
                    {panel.electorate.length > 0 && <ElectorateCard panel={panel} party={party} />}
                  </div>
                  <MyPartyCard
                    panel={panel}
                    party={party}
                    nickname={nickname}
                    onEditTicket={() => setDialog("ticket")}
                    onEditPromises={() => setDialog("promises")}
                    onChangeContribution={() => setDialog("contribution")}
                    onExpel={setExpelling}
                    onLeave={() => setDialog("leave")}
                  />
                </div>
              </div>
            </TabsContent>
          </Tabs>
        ) : (
          race
        ))}

      {/* Diálogos */}
      <FoundPartyDialog
        open={dialog === "found"}
        onOpenChange={close}
        panel={panel}
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
            current={mine.contribution}
            cash={cash}
          />
          <TicketDialog open={dialog === "ticket"} onOpenChange={close} party={party} panel={panel} cash={cash} />
          {mine.is_founder && (
            <PromisesDialog open={dialog === "promises"} onOpenChange={close} abbr={party.abbr} groups={panel.groups} />
          )}
          <LeavePartyDialog
            open={dialog === "leave"}
            onOpenChange={close}
            party={party}
            isFounder={mine.is_founder}
            isVice={panel.my_vice?.party_id === party.id && panel.my_vice.phase === "ACCEPTED"}
          />
          <ExpelDialog nickname={expelling} onClose={() => setExpelling(null)} party={party} />
          {mine.is_founder && party.flags === null && (
            <ChooseFlagsDialog open={dialog === "flags"} onOpenChange={close} panel={panel} party={party} />
          )}
        </>
      )}
      <ViceInviteDialog open={dialog === "vice"} onOpenChange={close} panel={panel} />
      <DonateDialog open={dialog === "donate"} onOpenChange={close} panel={panel} cash={cash} />
    </div>
  );
}
