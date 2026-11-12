import {
  Flag,
  Handshake,
  LogOut,
  Megaphone,
  PiggyBank,
  ScrollText,
  UserMinus,
  UserPlus,
  Vote,
  FilePlus2,
} from "lucide-react";
import { Link } from "react-router-dom";
import { Badge } from "@/shared/components/ui/badge";
import { displayDayMonth, displayList, displayShortDate } from "@/shared/lib/utils/display";
import type { ElectionPanel, ElectionParty } from "@/types";
import { electionPending } from "../lib/actions";
import { monthYear } from "../lib/election";
import { ActionGroup, DecideNow } from "./action-card";
import { ActionRow } from "./action-row";

/** Os diálogos da Eleição que as linhas abrem: o mesmo diálogo que a aba Campanha do partido abre. */
type ElectionActionDialog = "ticket" | "promises" | "contribution" | "leave" | "federation-propose";

type ElectionActionsTabProps = {
  panel: ElectionPanel;
  party: ElectionParty;
  mine: NonNullable<ElectionPanel["my_party"]>;
  onDialog: (dialog: ElectionActionDialog) => void;
  /** Leva à aba Campanha do partido, onde moram as ações sem diálogo próprio */
  onCampaign: () => void;
};

/** Suas ações na Eleição: o que o filiado e o fundador fazem na campanha, num lugar só; cada linha abre o diálogo ou leva à aba onde a ação mora. */
export function ElectionActionsTab({ panel, party, mine, onDialog, onCampaign }: ElectionActionsTabProps) {
  const pending = electionPending(panel);
  const pendingCount = (pending.vice ? 1 : 0) + (pending.promises ? 1 : 0);
  const { dates } = panel;
  const abbr = party.abbr;
  const isFounder = mine.is_founder;
  const campaignOpen = panel.phase === "CAMPAIGN" || panel.phase === "BETWEEN_ROUNDS";
  const governing = panel.term?.party_id === party.id;
  const deadline = displayDayMonth(dates.ticket_deadline);
  // A chapa só se inscreve com a campanha aberta e até o prazo do 1º turno
  const ticketClosed = panel.can_edit_ticket
    ? undefined
    : campaignOpen
      ? `O prazo da chapa fechou em ${displayShortDate(dates.ticket_deadline)}`
      : `Abre com a campanha, em ${monthYear(dates.campaign_start)}`;
  const inauguration = displayShortDate(dates.inauguration);

  // Os rivais que já prometeram medidas dão a régua de quem decide a chapa
  const rivalsWithPromises = panel.parties
    .filter((candidate) => candidate.id !== party.id && candidate.promises.length > 0)
    .map((candidate) => candidate.abbr);
  const otherMembers = party.members.filter((member) => !member.is_founder);

  return (
    <div className="grid gap-5 pt-3">
      {pendingCount > 0 && (
        <DecideNow count={pendingCount}>
          {pending.vice && (
            <ActionRow
              title={`A chapa do ${abbr} está sem vice`}
              chip={`até ${deadline}`}
              description="Convide um jogador da sala; ele precisa aceitar o convite."
              alsoIn="o aviso no topo da Eleição"
              actionLabel="Convidar vice"
              primary
              onAction={() => onDialog("ticket")}
            />
          )}
          {pending.promises && (
            <ActionRow
              title="A chapa ainda não prometeu nada"
              chip={`até ${deadline}`}
              description={`${rivalsWithPromises.length > 0 ? `${displayList(rivalsWithPromises)} já ${rivalsWithPromises.length === 1 ? "prometeu" : "prometeram"} medidas. ` : ""}Promessa mexe na intenção de voto dos grupos.`}
              alsoIn={`Campanha do ${abbr} › Seu partido`}
              actionLabel="Escolher promessas"
              primary
              onAction={() => onDialog("promises")}
            />
          )}
        </DecideNow>
      )}

      {/* Na campanha */}
      <ActionGroup title="Na campanha" subtitle={`Qualquer filiado do ${abbr} faz e paga da própria carteira`}>
        <ActionRow
          icon={Megaphone}
          title="Fazer uma ação de campanha"
          description="TV, evento com um grupo, comício ou ataque ao rival, pagos da sua carteira."
          alsoIn={`Campanha do ${abbr} › Ações de campanha`}
          actionLabel="Escolher ação"
          primary
          blockedReason={campaignOpen ? undefined : `Abre com a campanha, em ${monthYear(dates.campaign_start)}`}
          onAction={onCampaign}
        />
        <ActionRow
          icon={PiggyBank}
          title={`Contribuição ao ${abbr}`}
          description="Quanto da sua renda vai para a verba do partido todo mês."
          alsoIn={`Campanha do ${abbr} › Seu partido`}
          actionLabel="Ajustar"
          onAction={() => onDialog("contribution")}
        />
        <ActionRow
          icon={LogOut}
          title={`Sair do ${abbr}`}
          description="Você deixa a chapa e a bancada; o partido continua."
          alsoIn={`Campanha do ${abbr} › Seu partido`}
          actionLabel="Sair"
          onAction={() => onDialog("leave")}
        />
      </ActionGroup>

      {/* Depois da posse */}
      {!governing && (
        <ActionGroup
          title={`Depois da posse, se o ${abbr} vencer`}
          subtitle="Fica à vista para você saber o que a vitória destrava"
          aside={<Badge variant="secondary">Bloqueado até a posse</Badge>}
        >
          <ActionRow
            icon={FilePlus2}
            title="Nova medida"
            description="Muda impostos e gastos ou cria um programa."
            alsoIn="Governo › Suas ações"
            actionLabel="Nova medida"
            blockedReason={`Abre na posse, em ${inauguration}`}
            onAction={() => undefined}
          />
          <ActionRow
            icon={Vote}
            title="Orientar votações no Congresso"
            description={`A bancada eleita do ${abbr} vota como você orientar.`}
            alsoIn="Governo › Congresso"
            actionLabel="Orientar"
            blockedReason={`Abre com a bancada eleita, em ${inauguration}`}
            onAction={() => undefined}
          />
        </ActionGroup>
      )}

      {/* Como fundador */}
      {isFounder && (
        <ActionGroup
          title={`Como fundador do ${abbr}`}
          subtitle="Quem fundou o partido monta a chapa, promete e lidera a bancada"
        >
          <ActionRow
            icon={ScrollText}
            title="Promessas da chapa"
            description={`As medidas que o ${abbr} promete votar se vencer; cada uma tem custo de campanha.`}
            alsoIn={`Campanha do ${abbr} › Seu partido`}
            actionLabel="Escolher"
            blockedReason={panel.can_edit_ticket || panel.runoff_race?.can_add_promise ? undefined : ticketClosed}
            onAction={() => onDialog("promises")}
          />
          <ActionRow
            icon={UserMinus}
            title="Expulsar um filiado"
            description={`Tira um jogador do ${abbr}.`}
            alsoIn={`Campanha do ${abbr} › Seu partido`}
            actionLabel="Expulsar"
            blockedReason={otherMembers.length > 0 ? undefined : `O ${abbr} só tem você de filiado`}
            onAction={onCampaign}
          />
          <ActionRow
            icon={UserPlus}
            title="Montar a chapa"
            description={`Convida ou retira o vice. A chapa se inscreve até ${deadline}.`}
            alsoIn={`Campanha do ${abbr} › Seu partido`}
            actionLabel="Montar"
            blockedReason={ticketClosed}
            onAction={() => onDialog("ticket")}
          />
          <ActionRow
            icon={Flag}
            title="Orientação padrão da bancada"
            description="Sim ou Não por bandeira, para as votações que você não orientar."
            alsoIn={`Campanha do ${abbr} › Seu partido`}
            actionLabel="Ajustar"
            onAction={onCampaign}
          />
          <ActionRow
            icon={Handshake}
            title="Propor federação"
            description={`Junta o ${abbr} a outro partido na eleição e no Congresso.`}
            alsoIn={`Campanha do ${abbr} › Federação`}
            actionLabel="Propor"
            blockedReason={
              panel.can_federate ? undefined : (panel.federation_block ?? "A federação não está aberta agora")
            }
            onAction={() => onDialog("federation-propose")}
          />
        </ActionGroup>
      )}

      {/* Rodapé */}
      <p className="text-[13px] text-muted-foreground">
        Medidas, contas e Congresso ficam no Governo depois da posse.{" "}
        <Link to="/government" className="font-medium text-info hover:underline">
          Governo › Suas ações
        </Link>
      </p>
    </div>
  );
}
