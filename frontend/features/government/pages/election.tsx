import { useState } from "react";
import { useLocation } from "react-router-dom";
import {
  Flag,
  Handshake,
  Lock,
  MailQuestion,
  UserPlus,
  HandCoins,
  Megaphone,
  PiggyBank,
  ScrollText,
} from "lucide-react";
import { CardState } from "@/shared/components/card-state";
import { Alert, AlertAction, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { cn } from "@/shared/lib/utils";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/shared/components/ui/tabs";
import usePageLabel from "@/shared/hooks/usePageLabel";
import { usePortfolio } from "@/shared/hooks/queries/usePortfolio";
import { useRoomPlayers } from "@/shared/hooks/queries/useRoomPlayers";
import { useAuth } from "@/shared/hooks/useAuth";
import { displayDayMonth } from "@/shared/lib/utils/display";
import type { ElectionPanel, ElectionParty } from "@/types";
import { CampaignOpenedDialog } from "../components/campaign-opened-dialog";
import { CampaignSection } from "../components/campaign-section";
import { CampaignNotMember } from "../components/campaign-states";
import { ChooseFlagsDialog } from "../components/choose-flags-dialog";
import { ContributionDialog } from "../components/contribution-dialog";
import { DonateDialog } from "../components/donate-dialog";
import { FirstRoundCard } from "../components/first-round-card";
import { EndorseDialog } from "../components/endorse-dialog";
import { ElectionActionsTab } from "../components/election-actions-tab";
import { ElectionHeader } from "../components/election-header";
import { BeforeCampaignEmpty } from "../components/election-states";
import { ExpelDialog } from "../components/expel-dialog";
import { FederationAnswerDialog } from "../components/federation-answer-dialog";
import { FederationLeaveDialog } from "../components/federation-leave-dialog";
import { FederationProposeDialog } from "../components/federation-propose-dialog";
import { FoundPartyDialog } from "../components/found-party-dialog";
import { JoinPartyDialog } from "../components/join-party-dialog";
import { LeavePartyDialog } from "../components/leave-party-dialog";
import { PartyProfilesCard } from "../components/party-profiles-card";
import { PartyRegionsCard } from "../components/party-regions-card";
import { PollCard } from "../components/poll-card";
import { PromisesDialog } from "../components/promises-dialog";
import { RankingCard } from "../components/ranking-card";
import { RunoffContributionDialog } from "../components/runoff-contribution-dialog";
import { RunoffGroupsCard } from "../components/runoff-groups-card";
import { RunoffNotices } from "../components/runoff-notices";
import { RunoffPollCard } from "../components/runoff-poll-card";
import { TermCard } from "../components/term-card";
import { TicketDialog } from "../components/ticket-dialog";
import { ViceInviteDialog } from "../components/vice-invite-dialog";
import { useWithdrawFederation } from "../hooks/mutations/useWithdrawFederation";
import { electionPending, electionPendingCount } from "../lib/actions";
import { federationOf } from "../lib/federation";
import { affiliationNote, campaignEnded, collectionNote, type ElectionShortcut } from "../lib/election";
import { useElection } from "@/shared/hooks/queries/useElection";

export default function ElectionPage() {
  usePageLabel("Eleição");
  const { data: panel, error, refetch } = useElection();
  const location = useLocation();
  const state = location.state as { dialog?: ElectionShortcut; tab?: Tab } | null;

  if (!panel) {
    return (
      <CardState
        bare
        label="Carregando a eleição"
        error={error}
        onRetry={() => void refetch()}
        errorTitle="Não deu para carregar a eleição"
      >
        <Skeleton className="h-44" />
        <div className="grid items-start gap-5 xl:grid-cols-[minmax(0,1fr)_380px]">
          <div className="grid gap-5">
            <Card>
              <CardContent>
                <div className="grid gap-3">
                  <Skeleton className="h-3.5 w-2/5" />
                  <Skeleton className="h-50" />
                  <Skeleton className="h-3 w-[70%]" />
                </div>
              </CardContent>
            </Card>
            <Skeleton className="h-64" />
          </div>
          <Skeleton className="h-96" />
        </div>
      </CardState>
    );
  }

  // Cada navegação remonta a página, e o atalho de quem chegou pelo aviso da campanha abre o diálogo
  return (
    <ElectionContent
      key={location.key}
      panel={panel}
      initialDialog={state?.dialog ?? null}
      initialTab={state?.tab ?? "actions"}
    />
  );
}

type Dialog =
  | "found"
  | "join"
  | "contribution"
  | "ticket"
  | "promises"
  | "vice"
  | "campaign"
  | "leave"
  | "donate"
  | "flags"
  | "endorse"
  | "runoff-contribution"
  | "federation-propose"
  | "federation-answer"
  | "federation-leave";
type Tab = "actions" | "race" | "campaign";

type ElectionContentProps = { panel: ElectionPanel; initialDialog: Dialog | null; initialTab: Tab };

function ElectionContent({ panel, initialDialog, initialTab }: ElectionContentProps) {
  const { user } = useAuth();
  const { data: portfolio } = usePortfolio();
  const { data: players } = useRoomPlayers();
  const [dialog, setDialog] = useState<Dialog | null>(initialDialog);
  const [joinPartyId, setJoinPartyId] = useState<number | undefined>();
  // A proposta de federação aberta no diálogo de resposta; sem escolha, vale a primeira recebida
  const [answeringProposalId, setAnsweringProposalId] = useState<number | null>(null);
  const [expelling, setExpelling] = useState<string | null>(null);
  const [tab, setTab] = useState<Tab>(initialTab);
  const withdraw = useWithdrawFederation();

  const cash = portfolio?.cash;
  const nickname = user?.nickname ?? "";
  const mine = panel.my_party;
  const party = mine ? panel.parties.find((candidate) => candidate.id === mine.party_id) : undefined;
  const playerParties = panel.parties.filter((candidate) => !candidate.is_computer);
  const takenParties = panel.parties.flatMap((candidate) =>
    candidate.color ? [{ color: candidate.color, abbr: candidate.abbr }] : [],
  );
  const campaignOpen = panel.phase !== "BEFORE_CAMPAIGN";
  const hasTerm = panel.term !== null || panel.pending_term !== null;

  const close = (open: boolean) => !open && setDialog(null);
  const openJoin = (partyId?: number) => {
    setJoinPartyId(partyId);
    setDialog("join");
  };

  // As chapas que convidaram quem vê para vice, do partido dele ou de outro
  const invitingParties = panel.my_vices
    .filter((vice) => vice.phase === "PENDING")
    .map((vice) => panel.parties.find((candidate) => candidate.id === vice.party_id))
    .filter((candidate): candidate is ElectionParty => candidate !== undefined);

  // Vaga de vice aberta: a chapa tem candidato e ainda não tem vice nem convite pendente
  const viceOpen =
    !!party && !!mine?.is_founder && panel.can_edit_ticket && party.vice === null && party.vice_phase === "NONE";

  // A federação do partido de quem vê e as propostas abertas dele
  const federation = party ? federationOf(panel.federations, party.id) : undefined;
  const receivedProposals = panel.received_proposals;
  const answeringProposal =
    receivedProposals.find((proposal) => proposal.id === answeringProposalId) ?? receivedProposals[0];
  const sentProposal = panel.sent_proposal;
  const sentTo = panel.parties.find((candidate) => candidate.id === sentProposal?.to_party_id);

  // O selo da aba Suas ações conta as decisões da chapa que têm prazo
  const pendingCount = electionPendingCount(electionPending(panel));

  // A disputa do 2º turno, quando há
  const runoffRace = panel.runoff_race;

  const runoffFinalists = (runoffRace?.finalists ?? [])
    .map((id) => panel.parties.find((candidate) => candidate.id === id))
    .filter((candidate): candidate is ElectionParty => candidate !== undefined);

  // O 2º turno já apurado, que a página guarda por grupo até a próxima campanha
  const runoffResult = campaignEnded(panel.phase) && panel.last_result?.round === 2 ? panel.last_result : null;

  // A corrida é pública: quem não é filiado vê só ela, sem a barra de abas
  const race = (
    <div className="grid gap-5">
      {panel.runoff_race && <RunoffPollCard panel={panel} race={panel.runoff_race} />}
      {panel.runoff_race && <FirstRoundCard panel={panel} race={panel.runoff_race} finalists={runoffFinalists} />}
      {runoffResult && <RunoffGroupsCard panel={panel} result={runoffResult} />}
      {/* Entre os turnos a pesquisa vigente é a do 2º turno; a do 1º volta ao ar depois da apuração final */}
      {campaignOpen && !panel.runoff_race && <PollCard panel={panel} />}
      {campaignOpen && !panel.runoff_race && <PartyRegionsCard />}
      {/* Com mandato, o cartão dele fica ao lado dos partidos; sem, os partidos usam a largura toda */}
      <div className={cn("grid items-start gap-5", hasTerm && "xl:grid-cols-[minmax(0,1fr)_380px]")}>
        <div className="min-w-0">{panel.parties.length > 0 && <PartyProfilesCard panel={panel} />}</div>
        <TermCard panel={panel} />
      </div>
      <RankingCard panel={panel} />
    </div>
  );

  return (
    <div className="grid gap-5">
      <ElectionHeader panel={panel} onJoin={() => openJoin()} onFound={() => setDialog("found")} />

      {invitingParties.length > 0 && (
        <Alert variant="info">
          <MailQuestion />
          <AlertTitle>
            {invitingParties.length === 1 && invitingParties[0]
              ? `${invitingParties[0].founder ?? invitingParties[0].name} convidou você para vice no ${invitingParties[0].abbr}`
              : `${invitingParties.length} chapas convidaram você para vice: ${invitingParties.map((candidate) => candidate.abbr).join(", ")}`}
          </AlertTitle>
          <AlertDescription>
            Aceite ou recuse até {displayDayMonth(panel.dates.ticket_deadline)}; sem resposta, a chapa concorre sem
            vice.
            {invitingParties.length > 1 && " Aceitar um convite recusa os outros."}
          </AlertDescription>
          <AlertAction>
            <Button size="sm" onClick={() => setDialog("vice")}>
              Responder
            </Button>
          </AlertAction>
        </Alert>
      )}

      {party &&
        receivedProposals.map((proposal) => (
          <Alert key={proposal.id} variant="info">
            <Handshake />
            <AlertTitle>
              O {panel.parties.find((candidate) => candidate.id === proposal.from_party_id)?.abbr} propõe federação ao{" "}
              {party.abbr}
            </AlertTitle>
            <AlertDescription>
              Responda até {displayDayMonth(proposal.expires_on)}; sem resposta, a proposta expira. Também está em
              Pendências.
              {receivedProposals.length > 1 && " Aceitar uma recusa as outras e retira a que você enviou."}
            </AlertDescription>
            <AlertAction>
              <Button
                size="sm"
                onClick={() => {
                  setAnsweringProposalId(proposal.id);
                  setDialog("federation-answer");
                }}
              >
                Responder
              </Button>
            </AlertAction>
          </Alert>
        ))}

      {party && sentProposal && sentTo && (
        <Alert variant="info">
          <Handshake />
          <AlertTitle>Proposta enviada ao {sentTo.abbr}</AlertTitle>
          <AlertDescription>
            {sentProposal.name} · o {sentTo.abbr} responde até {displayDayMonth(sentProposal.expires_on)}.
          </AlertDescription>
          {panel.can_federate && (
            <AlertAction>
              <Button size="sm" variant="outline" disabled={withdraw.isPending} onClick={() => withdraw.mutate()}>
                Retirar
              </Button>
            </AlertAction>
          )}
        </Alert>
      )}

      {viceOpen && (
        <Alert variant="warning">
          <UserPlus />
          <AlertTitle>A chapa do {party.abbr} está sem vice</AlertTitle>
          <AlertDescription>
            Convide um jogador da sala até {displayDayMonth(panel.dates.ticket_deadline)}; ele precisa aceitar o
            convite.
          </AlertDescription>
          <AlertAction>
            <Button size="sm" variant="outline" onClick={() => setDialog("ticket")}>
              Convidar vice
            </Button>
          </AlertAction>
        </Alert>
      )}

      {runoffRace && <RunoffNotices panel={panel} race={runoffRace} />}

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

      {party && mine && runoffRace && (
        <>
          {runoffRace.can_declare && (
            <Alert variant="warning">
              <Megaphone />
              <AlertTitle>O {party.abbr} ficou fora: declare apoio a um finalista ou fique neutro</AlertTitle>
              <AlertDescription>
                Até {displayDayMonth(panel.dates.donation_deadline)}. Seus eleitores indecisos seguem a indicação na
                proporção da confiança que o grupo tem no {party.abbr}.
              </AlertDescription>
              <AlertAction>
                <Button size="sm" onClick={() => setDialog("endorse")}>
                  Declarar
                </Button>
              </AlertAction>
            </Alert>
          )}
          {runoffRace.can_contribute && (
            <Alert variant="info">
              <PiggyBank />
              <AlertTitle>Contribua uma vez com a campanha do {party.abbr} no 2º turno</AlertTitle>
              <AlertDescription>
                Até {displayDayMonth(panel.dates.donation_deadline)}. O valor sai do seu caixa de uma vez e vira verba
                do partido.
              </AlertDescription>
              <AlertAction>
                <Button size="sm" onClick={() => setDialog("runoff-contribution")}>
                  Contribuir
                </Button>
              </AlertAction>
            </Alert>
          )}
          {runoffRace.can_add_promise && (
            <Alert variant="info">
              <ScrollText />
              <AlertTitle>
                O {party.abbr} tem {party.promises.length} de {runoffRace.promise_limit} promessas
              </AlertTitle>
              <AlertDescription>
                No 2º turno as promessas só se acrescentam: as que já foram feitas ficam como estão.
              </AlertDescription>
              <AlertAction>
                <Button size="sm" variant="outline" onClick={() => setDialog("promises")}>
                  Acrescentar
                </Button>
              </AlertAction>
            </Alert>
          )}
        </>
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

      {/* O partido existe desde o 1º dia: antes da campanha, a página já serve a quem tem ou pode ter partido */}
      {!campaignOpen && !hasTerm && !mine && !panel.can_found_or_join && <BeforeCampaignEmpty panel={panel} />}

      {(campaignOpen || hasTerm || mine || panel.can_found_or_join) &&
        (party && mine ? (
          <Tabs value={tab} onValueChange={(value) => setTab(value as Tab)}>
            <TabsList variant="line">
              <TabsTrigger value="actions">
                Suas ações
                {pendingCount > 0 && (
                  <Badge variant="warning" size="sm" aria-label={`${pendingCount} decisões com prazo`}>
                    {pendingCount}
                  </Badge>
                )}
              </TabsTrigger>
              <TabsTrigger value="race">Corrida</TabsTrigger>
              <TabsTrigger value="campaign">Campanha do {party.abbr}</TabsTrigger>
            </TabsList>
            <TabsContent value="actions">
              <ElectionActionsTab
                panel={panel}
                party={party}
                mine={mine}
                onDialog={setDialog}
                onCampaign={() => setTab("campaign")}
              />
            </TabsContent>
            <TabsContent value="race">{race}</TabsContent>
            <TabsContent value="campaign">
              <CampaignSection
                panel={panel}
                party={party}
                nickname={nickname}
                onEditTicket={() => setDialog("ticket")}
                onEditPromises={() => setDialog("promises")}
                onChangeContribution={() => setDialog("contribution")}
                onExpel={setExpelling}
                onLeave={() => setDialog("leave")}
                onProposeFederation={() => setDialog("federation-propose")}
                onLeaveFederation={() => setDialog("federation-leave")}
              />
            </TabsContent>
          </Tabs>
        ) : (
          <div className="grid gap-5">
            {panel.can_found_or_join && (
              <CampaignNotMember
                canJoin={playerParties.length > 0}
                deadline={affiliationNote(panel)}
                onJoin={() => openJoin()}
                onFound={() => setDialog("found")}
              />
            )}
            {race}
          </div>
        ))}

      {/* Diálogos */}
      <FoundPartyDialog
        open={dialog === "found"}
        onOpenChange={close}
        panel={panel}
        taken={takenParties}
        founderColor={players?.find((player) => player.nickname === nickname)?.color}
        cash={cash}
      />
      <JoinPartyDialog
        open={dialog === "join"}
        onOpenChange={close}
        parties={playerParties}
        initialPartyId={joinPartyId}
        cash={cash}
        collectionNote={collectionNote(panel)}
      />
      {party && mine && (
        <>
          <ContributionDialog
            open={dialog === "contribution"}
            onOpenChange={close}
            party={party}
            current={mine.contribution}
            currentCongress={mine.congress}
            cash={cash}
            collectionNote={collectionNote(panel)}
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
            isVice={panel.my_vices.some((vice) => vice.party_id === party.id && vice.phase === "ACCEPTED")}
          />
          <FederationProposeDialog
            open={dialog === "federation-propose"}
            onOpenChange={close}
            panel={panel}
            party={party}
          />
          {answeringProposal && (
            <FederationAnswerDialog
              open={dialog === "federation-answer"}
              onOpenChange={close}
              panel={panel}
              party={party}
              proposal={answeringProposal}
            />
          )}
          {federation && (
            <FederationLeaveDialog open={dialog === "federation-leave"} onOpenChange={close} federation={federation} />
          )}
          <ExpelDialog nickname={expelling} onClose={() => setExpelling(null)} party={party} />
          {mine.is_founder && party.flags === null && (
            <ChooseFlagsDialog open={dialog === "flags"} onOpenChange={close} panel={panel} party={party} />
          )}
        </>
      )}
      <ViceInviteDialog open={dialog === "vice"} onOpenChange={close} panel={panel} />
      <CampaignOpenedDialog
        open={dialog === "campaign"}
        onOpenChange={close}
        panel={panel}
        onShortcut={(shortcut) => (shortcut === "join" ? openJoin() : setDialog(shortcut))}
      />
      <DonateDialog open={dialog === "donate"} onOpenChange={close} panel={panel} cash={cash} />
      {party && runoffRace && (
        <>
          <EndorseDialog
            open={dialog === "endorse"}
            onOpenChange={close}
            panel={panel}
            race={runoffRace}
            party={party}
          />
          <RunoffContributionDialog
            open={dialog === "runoff-contribution"}
            onOpenChange={close}
            panel={panel}
            race={runoffRace}
            party={party}
            cash={cash}
          />
        </>
      )}
    </div>
  );
}
