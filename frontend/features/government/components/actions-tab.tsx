import {
  Coins,
  FilePlus2,
  Handshake,
  Landmark,
  Megaphone,
  Percent,
  PiggyBank,
  ScrollText,
  Siren,
  UserPlus,
  Vote,
} from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { CardState } from "@/shared/components/card-state";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from "@/shared/components/ui/empty";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { useElection } from "@/shared/hooks/queries/useElection";
import { usePortfolio } from "@/shared/hooks/queries/usePortfolio";
import { displayDayMonth, displayShortDate } from "@/shared/lib/utils/display";
import type { ElectionPanel, GovernmentPanel, MeasureKind } from "@/types";
import { governmentPending } from "../lib/actions";
import { unguidedCount } from "../lib/house";
import { affiliationNote, collectionNote, monthYear } from "../lib/election";
import { ActionGroup, DecideNow } from "./action-card";
import { ActionRow } from "./action-row";
import { ContributionDialog } from "./contribution-dialog";
import { FederationProposeDialog } from "./federation-propose-dialog";
import { RequestImpeachmentDialog } from "./request-impeachment-card";

type GovernmentTab = "mandate" | "accounts" | "congress";

type ActionsTabProps = {
  panel: GovernmentPanel;
  /** Abre a Nova medida, já no tipo da medida quando vem um */
  onPropose: (kind?: MeasureKind) => void;
  /** Leva a outra aba do Governo */
  onGo: (tab: GovernmentTab) => void;
};

/** Suas ações: o que o jogador faz no Governo e na bancada, num lugar só; cada linha abre o diálogo ou leva à aba onde a ação mora. */
export function ActionsTab({ panel, onPropose, onGo }: ActionsTabProps) {
  const { data: election, error, refetch } = useElection();

  if (!election) {
    return (
      <div className="pt-3">
        <CardState
          bare
          label="Carregando suas ações"
          error={error}
          onRetry={() => void refetch()}
          errorTitle="Não deu para carregar suas ações"
          errorDescription="Nada se perdeu: as decisões já tomadas estão salvas."
        >
          {Array.from({ length: 3 }, (_, index) => (
            <Card key={index} size="flush">
              <div className="grid gap-3 px-5 py-4">
                <Skeleton className="h-4 w-44" />
                <Skeleton className="h-9" />
                <Skeleton className="h-9" />
              </div>
            </Card>
          ))}
        </CardState>
      </div>
    );
  }

  return (
    <div className="pt-3">
      <ActionsContent panel={panel} election={election} onPropose={onPropose} onGo={onGo} />
    </div>
  );
}

type ActionsContentProps = ActionsTabProps & { election: ElectionPanel };
type Dialog = "contribution" | "impeachment" | "federation";

function ActionsContent({ panel, election, onPropose, onGo }: ActionsContentProps) {
  const navigate = useNavigate();
  const { data: portfolio } = usePortfolio();
  const [dialog, setDialog] = useState<Dialog | null>(null);
  const close = (open: boolean) => !open && setDialog(null);

  const mine = election.my_party;
  const party = mine ? election.parties.find((candidate) => candidate.id === mine.party_id) : undefined;
  const pending = governmentPending(panel);
  const pendingCount = (pending.unguided ? 1 : 0) + (pending.idlePromises ? 1 : 0);

  const toElection = (state?: { tab?: "campaign"; dialog?: "join" | "found" }) => void navigate("/election", { state });

  if (!mine || !party) {
    return <WithoutParty election={election} onElection={toElection} />;
  }

  const isLeader = mine.is_founder;
  const governing = election.parties.find((candidate) => candidate.id === election.term?.party_id);
  const opposition = governing !== undefined && governing.id !== party.id;
  const campaignOpen = election.phase === "CAMPAIGN" || election.phase === "BETWEEN_ROUNDS";
  const leaderName = party.founder ? `, ${party.founder},` : "";
  const notLeaderReason = `Só o líder do ${party.abbr}${leaderName} orienta a bancada`;

  const impeachmentBlock = panel.is_president
    ? "Você é o presidente: o pedido seria contra o seu governo"
    : panel.congress.can_request_impeachment
      ? undefined
      : (panel.congress.impeachment_block ?? "O pedido não está aberto agora");

  return (
    <div className="grid gap-5">
      {pendingCount > 0 && (
        <DecideNow count={pendingCount}>
          {pending.unguided && (
            <ActionRow
              title={
                pending.unguided.count === 1
                  ? "Medida a caminho do plenário sem orientação"
                  : `${pending.unguided.count} medidas a caminho do plenário sem orientação`
              }
              chip={pending.unguided.date ? `vota em ${displayDayMonth(pending.unguided.date)}` : undefined}
              description={`Sem orientação, a bancada do ${party.abbr} vota pela orientação padrão.`}
              alsoIn="Congresso › Medidas a caminho"
              actionLabel="Orientar a bancada"
              primary
              onAction={() => onGo("congress")}
            />
          )}
          {pending.idlePromises && (
            <ActionRow
              title={
                pending.idlePromises.titles.length === 1
                  ? "1 promessa da chapa sem andar"
                  : `${pending.idlePromises.titles.length} promessas da chapa sem andar`
              }
              chip={`até ${displayDayMonth(pending.idlePromises.lastVote)}`}
              description={`${pending.idlePromises.titles.join(", ")}. A votação de ${displayDayMonth(pending.idlePromises.lastVote)} é a última que conta para elas.`}
              alsoIn="Mandato › Promessas da chapa"
              actionLabel="Propor a medida"
              primary
              onAction={() => onPropose(pending.idlePromises?.kind)}
            />
          )}
        </DecideNow>
      )}

      {/* Como presidente */}
      {panel.is_president && (
        <ActionGroup
          title="Como presidente"
          subtitle={`Você governa${panel.term_end ? ` até ${monthYear(panel.term_end)}` : ""}: medidas, gastos e apoio no Congresso`}
        >
          <ActionRow
            icon={FilePlus2}
            title="Nova medida"
            description="Muda impostos e gastos ou cria um programa. Vai a votação no Congresso."
            alsoIn="Contas › Impostos"
            actionLabel="Propor"
            primary
            onAction={() => onPropose()}
          />
          <ActionRow
            icon={Percent}
            title="Mudar um imposto"
            description="Do IR das pessoas ao IOF. Abre a Nova medida na aba de impostos."
            alsoIn="Contas › Impostos"
            actionLabel="Escolher"
            onAction={() => onPropose()}
          />
          <ActionRow
            icon={Coins}
            title="Mudar um gasto"
            description="Auxílio, Obras, Custeio e Reajustes. Abre a Nova medida na aba de gastos."
            alsoIn="Contas › Gasto público"
            actionLabel="Escolher"
            onAction={() => onPropose("WELFARE_SPENDING")}
          />
          {panel.promises && (
            <ActionRow
              icon={ScrollText}
              title="Cumprir as promessas da chapa"
              chip={pending.idlePromises ? `${pending.idlePromises.titles.length} sem andar` : undefined}
              description="As medidas que a chapa prometeu na campanha; cada uma aprovada no Congresso conta como cumprida."
              alsoIn="Mandato › Promessas da chapa"
              actionLabel="Ver promessas"
              onAction={() => onGo("mandate")}
            />
          )}
          <ActionRow
            icon={Landmark}
            title="Decidir a SELIC no Copom"
            description="Marca a SELIC da próxima reunião do Copom."
            alsoIn="Contas › SELIC"
            actionLabel="Decidir"
            blockedReason={panel.monetary?.by_government ? undefined : "A SELIC está com o Banco Central neste mandato"}
            onAction={() => onGo("accounts")}
          />
          <ActionRow
            icon={Handshake}
            title="Negociar apoio no Congresso"
            description="Troca cargos e emendas pelos votos da base."
            alsoIn="Contas › Base no Congresso"
            actionLabel="Negociar"
            onAction={() => onGo("accounts")}
          />
        </ActionGroup>
      )}

      {/* Como filiado */}
      {!isLeader && (
        <ActionGroup
          title={`Como filiado do ${party.abbr}`}
          subtitle={
            opposition
              ? `O governo é do ${governing.abbr}; o ${party.abbr} está na oposição`
              : `O ${party.abbr} está no governo`
          }
        >
          <ActionRow
            icon={PiggyBank}
            title={`Contribuição ao ${party.abbr}`}
            description="Quanto da sua renda vai para a verba do partido todo mês."
            alsoIn={`Eleição › Campanha do ${party.abbr}`}
            actionLabel="Ajustar"
            onAction={() => setDialog("contribution")}
          />
          <CampaignActionRow
            open={campaignOpen}
            opensOn={election.dates.campaign_start}
            onAction={() => toElection({ tab: "campaign" })}
          />
        </ActionGroup>
      )}

      {/* Como líder da bancada */}
      <ActionGroup
        title={`Como líder do ${party.abbr}`}
        subtitle={
          !isLeader
            ? "Quem fundou o partido lidera a bancada"
            : opposition
              ? `Você fundou o ${party.abbr} e lidera a bancada de oposição`
              : "Quem fundou o partido lidera a bancada: é você"
        }
      >
        <ActionRow
          icon={Vote}
          title="Orientar uma votação"
          chip={
            isLeader && pending.unguided ? `${unguidedCount(panel.congress, panel.queue)} sem orientação` : undefined
          }
          description={`Diz à bancada do ${party.abbr} como votar.`}
          alsoIn="Congresso › Medidas a caminho"
          actionLabel="Orientar"
          blockedReason={isLeader ? undefined : notLeaderReason}
          onAction={() => onGo("congress")}
        />
        {isLeader && (
          <>
            <ActionRow
              icon={UserPlus}
              title="Orientação padrão da bancada"
              description="Sim ou Não por bandeira, para as votações que você não orientar."
              alsoIn={`Eleição › Campanha do ${party.abbr} › Seu partido`}
              actionLabel="Ajustar"
              onAction={() => toElection({ tab: "campaign" })}
            />
            <ActionRow
              icon={Siren}
              title="Pedir o impeachment"
              description="Abre o processo contra quem governa; o Congresso vota."
              alsoIn="Congresso"
              actionLabel="Pedir"
              primary
              blockedReason={impeachmentBlock}
              onAction={() => setDialog("impeachment")}
            />
            <ActionRow
              icon={Handshake}
              title="Propor federação"
              description={`Junta o ${party.abbr} a outro partido na eleição e no Congresso.`}
              alsoIn={`Eleição › Campanha do ${party.abbr} › Federação`}
              actionLabel="Propor"
              blockedReason={
                election.can_federate ? undefined : (election.federation_block ?? "A federação não está aberta agora")
              }
              onAction={() => setDialog("federation")}
            />
          </>
        )}
      </ActionGroup>

      {/* Rodapé */}
      <p className="text-[13px] text-muted-foreground">
        Campanha, chapa e contribuição ao partido ficam na Eleição.{" "}
        <Link to="/election" className="font-medium text-info hover:underline">
          Eleição › Suas ações
        </Link>
      </p>

      {/* Diálogos */}
      <ContributionDialog
        open={dialog === "contribution"}
        onOpenChange={close}
        party={party}
        current={mine.contribution}
        currentCongress={mine.congress}
        cash={portfolio?.cash}
        collectionNote={collectionNote(election)}
      />
      <RequestImpeachmentDialog open={dialog === "impeachment"} onOpenChange={close} />
      <FederationProposeDialog open={dialog === "federation"} onOpenChange={close} panel={election} party={party} />
    </div>
  );
}

type CampaignActionRowProps = { open: boolean; opensOn: string; onAction: () => void; blockedReason?: string };

/** A ação de campanha: liberada com a campanha aberta; antes dela, a linha diz quando abre. */
function CampaignActionRow({ open, opensOn, onAction, blockedReason }: CampaignActionRowProps) {
  const reason = blockedReason ?? (open ? undefined : `Abre com a campanha, em ${monthYear(opensOn)}`);

  return (
    <ActionRow
      icon={Megaphone}
      title="Fazer uma ação de campanha"
      description="TV, evento, comício ou ataque ao rival, pagos da sua carteira."
      alsoIn="Eleição › Campanha"
      actionLabel="Escolher"
      blockedReason={reason}
      onAction={onAction}
    />
  );
}

type WithoutPartyProps = {
  election: ElectionPanel;
  onElection: (state?: { dialog?: "join" | "found" }) => void;
};

/** Quem não tem partido: o primeiro passo é a filiação, e o resto das ações fica à vista, apagado. */
function WithoutParty({ election, onElection }: WithoutPartyProps) {
  const navigate = useNavigate();

  if (!election.can_found_or_join) {
    return (
      <Card>
        <CardContent>
          <Empty>
            <EmptyMedia variant="icon">
              <Vote />
            </EmptyMedia>
            <EmptyHeader>
              <EmptyTitle>Nada para fazer agora</EmptyTitle>
              <EmptyDescription>
                O computador governa até a posse, e a campanha abre em {displayShortDate(election.dates.campaign_start)}
                . Até lá, a filiação a um partido não está aberta.
              </EmptyDescription>
            </EmptyHeader>
            <Button size="sm" variant="outline" onClick={() => void navigate("/election")}>
              Ver os partidos
            </Button>
          </Empty>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="grid gap-5">
      <Card>
        <CardContent>
          <div className="grid gap-3">
            <div className="flex items-center gap-2.5">
              <Vote className="size-[18px] text-primary" />
              <h2 className="text-[15px] font-semibold">Você ainda não tem partido</h2>
            </div>
            <span className="text-[13px] text-muted-foreground">
              Com um partido você faz campanha, promete medidas e pode chegar à presidência. {affiliationNote(election)}
            </span>
            <div className="flex flex-wrap gap-2">
              <Button size="sm" onClick={() => onElection({ dialog: "join" })}>
                Filiar-se a um partido
              </Button>
              <Button size="sm" variant="outline" onClick={() => onElection({ dialog: "found" })}>
                Fundar partido
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <ActionGroup title="Com um partido" subtitle="O que se abre depois da filiação">
        <CampaignActionRow
          open={false}
          opensOn={election.dates.campaign_start}
          blockedReason="Precisa de um partido"
          onAction={() => undefined}
        />
        <ActionRow
          icon={ScrollText}
          title="Promessas da chapa"
          description="As medidas que o partido promete votar se vencer a eleição."
          alsoIn="Eleição › Campanha do partido"
          actionLabel="Escolher"
          blockedReason="Precisa fundar um partido"
          onAction={() => undefined}
        />
      </ActionGroup>
    </div>
  );
}
