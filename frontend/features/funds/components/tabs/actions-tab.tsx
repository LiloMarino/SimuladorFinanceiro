import {
  Coins,
  FileText,
  Gavel,
  HandCoins,
  Handshake,
  Landmark,
  Megaphone,
  Percent,
  Undo2,
  UserPlus,
  Wallet,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { ActionGroup, DecideNow } from "@/shared/components/action-card";
import { ActionRow } from "@/shared/components/action-row";
import { useActiveAccount } from "@/shared/hooks/useActiveAccount";
import { fundStage } from "@/shared/lib/fund-view";
import {
  displayIsoDate,
  displayMoney,
  displayPercent,
  displayQuantity,
  displayShortDate,
} from "@/shared/lib/utils/display";
import type { FundDetails } from "@/types";
import { useAnswerComanagerInvite } from "../../hooks/mutations/useAnswerComanagerInvite";
import { useAnswerDirectedIssuance } from "../../hooks/mutations/useAnswerDirectedIssuance";
import { useCloseFundOffer } from "../../hooks/mutations/useCloseFundOffer";
import { blockReason } from "../../lib/fund-assembly";
import { MAX_COMANAGERS, type Comanager } from "../../lib/fund-comanagers";
import type { DirectedOffer } from "../../lib/fund-directed";
import { FIRST_QUOTA_PRICE } from "../../lib/fund-math";
import { fundPending, fundPendingCount } from "../../lib/fund-pending";
import type { FundTabActions } from "../../lib/fund-tabs";

type ActionsTabProps = { fund: FundDetails; userId: number; actions: FundTabActions };

const cashOf = (fund: FundDetails) => fund.composition.find((item) => item.asset_class === "cash")?.value ?? "0";

/** O convite de co-gestão: aceitar ou recusar na própria linha. */
function InviteRow({ fund, invite }: { fund: FundDetails; invite: Comanager }) {
  const answer = useAnswerComanagerInvite(fund.id);

  return (
    <ActionRow
      tone="fund"
      title={`Convite de co-gestão da ${fund.name}`}
      chip={invite.expires_on ? `até ${displayShortDate(invite.expires_on)}` : undefined}
      description={`${fund.manager_nickname ?? "O gestor"} chama você para operar a carteira junto e dividir as taxas: ${displayPercent(Number(invite.pending_share ?? 0), 0)} delas, a partir do mês seguinte ao aceite.`}
      secondaryLabel="Recusar"
      onSecondary={() => answer.mutate(false)}
      actionLabel="Aceitar"
      onAction={() => answer.mutate(true)}
      blockedReason={answer.isPending ? "Enviando a resposta" : undefined}
      primary
    />
  );
}

/** A oferta de cotas novas feita ao jogador: aceitar ou recusar na própria linha. */
function DirectedRow({ fund, offer }: { fund: FundDetails; offer: DirectedOffer }) {
  const answer = useAnswerDirectedIssuance(fund.id);

  return (
    <ActionRow
      tone="fund"
      title="Oferta de cotas novas"
      chip={`até ${displayShortDate(offer.expires_on)}`}
      description={`${fund.manager_nickname ?? "O gestor"} oferece ${displayQuantity(offer.quotas)} cotas novas da ${fund.name}, pagas do seu caixa pessoal ao preço e dentro do teto do dia em que você aceita.`}
      secondaryLabel="Recusar"
      onSecondary={() => answer.mutate(false)}
      actionLabel="Aceitar"
      onAction={() => answer.mutate(true)}
      blockedReason={answer.isPending ? "Enviando a resposta" : undefined}
      primary
    />
  );
}

/** Suas ações: o que o jogador decide e faz nesta gestora, num lugar só; cada linha abre o diálogo ou leva à aba onde a ação mora. */
export function ActionsTab({ fund, userId, actions }: ActionsTabProps) {
  const navigate = useNavigate();
  const { fund: activeFund, switchAccount } = useActiveAccount();
  const closeOffer = useCloseFundOffer(fund.id);

  const stage = fundStage(fund);
  const isManager = fund.my_role === "manager";
  const isComanager = fund.my_role === "comanager";
  const total = Number(fund.quotas);
  const mine = Number(fund.my_quotas);
  const share = total > 0 ? mine / total : 0;
  const nav = fund.nav === null ? FIRST_QUOTA_PRICE : Number(fund.nav);
  const operating = activeFund?.fund_id === fund.id;
  const payable = Number(fund.fees.payable);
  const issuanceOpenNow = fund.issuance !== null && fund.issuance.closed_on === null;
  const buybackOpenNow = fund.buyback?.state === "open";
  const assemblyOpenNow = fund.assembly.current !== null;
  const pending = fundPending(fund, userId);
  const pendingCount = fundPendingCount(pending);
  const issuance = fund.issuance;
  const conveneReason = blockReason(fund.assembly);
  const sellable = Number(fund.sellable_keeping_control ?? 0);
  const tradeUrl = `/variable-income/${fund.ticker}`;

  const operateRow = (
    <ActionRow
      tone="fund"
      icon={Wallet}
      title={operating ? "Voltar à minha carteira" : "Operar a carteira"}
      description={`Compre e venda ações e renda fixa pela conta da gestora. O caixa dela está em ${displayMoney(cashOf(fund))}${payable > 0 ? ` e ela deve ${displayMoney(payable)} de taxa a pagar` : ""}.`}
      {...(isManager ? { alsoIn: "Carteira" } : {})}
      actionLabel={operating ? "Voltar à minha carteira" : "Operar a carteira"}
      onAction={() => switchAccount(operating ? null : fund.id)}
      blockedReason={
        fund.frozen_until ? `A carteira está congelada até ${displayIsoDate(fund.frozen_until)}` : undefined
      }
      primary={!operating}
    />
  );

  return (
    <div className="grid gap-5 pt-3">
      {/* Para decidir agora */}
      {pendingCount > 0 && (
        <DecideNow count={pendingCount}>
          {pending.preferenceLeft > 0 && issuance && (
            <ActionRow
              tone="fund"
              title={`Preferência na emissão: até ${displayQuantity(String(pending.preferenceLeft))} cotas`}
              chip={`até ${displayShortDate(issuance.preference_ends_on)}`}
              description={`A ${fund.name} emitiu ${displayQuantity(issuance.quotas)} cotas novas a ${displayMoney(issuance.price)}. Com ${displayPercent(share, 1)} das cotas, você compra até ${displayQuantity(String(pending.preferenceLeft))} antes de todos; depois, a sobra abre a qualquer investidor. Sem comprar, sua fatia cai.`}
              alsoIn="Cotas"
              actionLabel="Comprar com preferência"
              onAction={() => actions.goTo("quotas")}
              primary
            />
          )}
          {pending.directed && <DirectedRow fund={fund} offer={pending.directed} />}
          {pending.invite && <InviteRow fund={fund} invite={pending.invite} />}
        </DecideNow>
      )}

      {/* Para abrir a gestora */}
      {stage === "closed" && isManager && (
        <ActionGroup
          title="Para abrir a gestora"
          subtitle={`Três passos, nesta ordem. A primeira cota vale ${displayMoney(FIRST_QUOTA_PRICE)} e só você tem cotas até a oferta.`}
        >
          <ActionRow
            tone="fund"
            icon={Coins}
            title="1. Levar da carteira"
            chip={total > 0 ? "feito" : undefined}
            chipVariant="success"
            description={
              total > 0
                ? `Leve mais caixa e ações da sua carteira em troca de cotas a ${displayMoney(nav)} cada. Você já tem ${displayQuantity(fund.my_quotas)} cotas.`
                : `Leve caixa e ações da sua carteira em troca de cotas a ${displayMoney(FIRST_QUOTA_PRICE)} cada. A gestora nasce sem caixa e sem cotas.`
            }
            actionLabel={total > 0 ? "Levar mais" : "Levar da carteira"}
            onAction={() => actions.open("contribute")}
            primary={total === 0}
          />
          <ActionRow
            tone="fund"
            icon={Percent}
            title="2. Conferir as taxas"
            description={`Administração de ${displayPercent(fund.management_fee, 1, { trim: true })} ao ano e performance de ${displayPercent(fund.performance_fee, 1, { trim: true })} sobre o que passar do CDI. Saem do patrimônio de todos os cotistas, você inclusive.`}
            alsoIn="Configurações"
            actionLabel="Conferir taxas"
            onAction={() => actions.open("fees")}
          />
          <ActionRow
            tone="fund"
            icon={Megaphone}
            title="3. Abrir a oferta pública"
            description={`Qualquer investidor compra cotas a ${displayMoney(nav)} enquanto a oferta durar. Quando ela fecha, a cota passa a ser negociada no mercado.`}
            actionLabel="Abrir a oferta"
            onAction={() => actions.open("offer")}
            blockedReason={total === 0 ? "Leve cotas da sua carteira antes de abrir a oferta" : undefined}
            primary={total > 0}
          />
        </ActionGroup>
      )}

      {/* Como gestor */}
      {isManager && stage !== "closed" && (
        <ActionGroup title="Como gestor" subtitle={`O que só quem gere a ${fund.name} faz`}>
          {operateRow}
          {stage === "offer" && (
            <ActionRow
              tone="fund"
              icon={Megaphone}
              title="Encerrar a oferta"
              description="Fecha a oferta pública agora, com o que já foi vendido. A cota passa a ser negociada no mercado."
              actionLabel="Encerrar a oferta"
              onAction={() => closeOffer.mutate()}
              blockedReason={closeOffer.isPending ? "Encerrando a oferta" : undefined}
            />
          )}
          {stage === "listed" && (
            <>
              <ActionRow
                tone="fund"
                icon={Megaphone}
                title="Emissão pública"
                description="Cotas novas ao patrimônio por cota do dia do anúncio: primeiro só os cotistas compram, na proporção do que têm, e a sobra abre a todos."
                actionLabel="Abrir emissão"
                onAction={() => actions.open("issuance")}
                blockedReason={
                  issuanceOpenNow
                    ? "Já há uma emissão aberta"
                    : buybackOpenNow
                      ? "Há uma recompra em aberto"
                      : assemblyOpenNow
                        ? "Há uma assembleia em votação"
                        : undefined
                }
              />
              <ActionRow
                tone="fund"
                icon={HandCoins}
                title="Emissão dirigida"
                description="Cotas novas para um co-gestor, pagas do caixa pessoal dele e liquidadas quando ele aceita."
                actionLabel="Emitir cotas"
                onAction={() => actions.open("directed")}
                blockedReason={
                  fund.directed_issuance !== null
                    ? "Há uma oferta dirigida esperando resposta"
                    : issuanceOpenNow
                      ? "Já há uma emissão aberta"
                      : buybackOpenNow
                        ? "Há uma recompra em aberto"
                        : assemblyOpenNow
                          ? "Há uma assembleia em votação"
                          : undefined
                }
              />
              <ActionRow
                tone="fund"
                icon={Landmark}
                title="Empréstimo em nome da gestora"
                description="A nota de crédito, os juros e o limite saem do patrimônio da gestora, e o dinheiro entra no caixa dela."
                alsoIn="Carteira"
                actionLabel="Pedir empréstimo"
                onAction={() => {
                  switchAccount(fund.id);
                  void navigate("/credit");
                }}
              />
              <ActionRow
                tone="fund"
                icon={Undo2}
                title="Recompra de cotas"
                description="A gestora compra as próprias cotas no livro com o caixa dela, e as cotas compradas deixam de existir."
                actionLabel="Recomprar"
                onAction={() => actions.open("buyback")}
                blockedReason={
                  total === 0
                    ? "A gestora não tem cotas"
                    : issuanceOpenNow
                      ? "Há uma emissão aberta"
                      : buybackOpenNow
                        ? "Há uma recompra em aberto"
                        : undefined
                }
              />
              <ActionRow
                tone="fund"
                icon={UserPlus}
                title="Convidar co-gestor"
                description="Divide a gestão e uma parte das taxas com outro jogador, que aceita na lista de pendências dele."
                alsoIn="Cotas"
                actionLabel="Convidar"
                onAction={() => actions.open("invite")}
                blockedReason={
                  fund.comanagers.length >= MAX_COMANAGERS
                    ? `A gestora já tem ${MAX_COMANAGERS} co-gestores`
                    : undefined
                }
              />
            </>
          )}
          <ActionRow
            tone="fund"
            icon={Percent}
            title="Mudar taxas"
            description={`Administração de ${displayPercent(fund.management_fee, 1, { trim: true })} ao ano e performance de ${displayPercent(fund.performance_fee, 1, { trim: true })} sobre o que passar do CDI.`}
            alsoIn="Configurações"
            actionLabel="Mudar taxas"
            onAction={() => actions.open("fees")}
          />
        </ActionGroup>
      )}

      {/* Como co-gestor */}
      {isComanager && (
        <ActionGroup
          title="Como co-gestor"
          subtitle={`Você opera a carteira e fica com ${displayPercent(Number(fund.my_share ?? 0), 0)} das taxas`}
        >
          {operateRow}
        </ActionGroup>
      )}

      {/* Como cotista */}
      <ActionGroup
        title={mine > 0 ? "Como cotista" : "Como investidor"}
        subtitle={
          mine > 0
            ? `Você tem ${displayQuantity(fund.my_quotas)} cotas (${displayPercent(share, 1)}), que valem ${displayMoney(fund.my_value)} pelo patrimônio por cota`
            : `Você ainda não tem cotas da ${fund.name}`
        }
      >
        <ActionRow
          tone="fund"
          icon={Handshake}
          title={stage === "offer" && !isManager ? "Comprar na oferta pública" : "Negociar a cota"}
          description={
            stage === "closed"
              ? `Comprar e vender ${fund.ticker} no livro, com outros investidores.`
              : stage === "offer"
                ? `A oferta vende cotas a ${fund.offer_price === null ? "—" : displayMoney(fund.offer_price)}${fund.offer_ends_on ? ` até ${displayIsoDate(fund.offer_ends_on)}` : ""}.`
                : `Compre ou venda ${fund.ticker} no livro${fund.price === null ? "" : `, a ${displayMoney(fund.price)} hoje`}.${
                    isManager && sellable > 0
                      ? ` Você vende até ${displayQuantity(String(sellable))} cotas sem perder o controle.`
                      : ""
                  }`
          }
          actionLabel={stage === "offer" && !isManager ? "Comprar" : "Negociar"}
          onAction={() => void navigate(tradeUrl)}
          blockedReason={stage === "closed" ? "A cota chega ao mercado quando a oferta pública fecha" : undefined}
          primary={!isManager}
        />
        {stage === "listed" && !isManager && (
          <ActionRow
            tone="fund"
            icon={Gavel}
            title="Convocar a assembleia"
            description="Quem tem 10% das cotas ou mais convoca os cotistas para trocar o gestor."
            alsoIn="Assembleia"
            actionLabel="Convocar"
            onAction={() => actions.goTo("assembly")}
            blockedReason={conveneReason ?? undefined}
          />
        )}
        {fund.last_report !== null && (
          <ActionRow
            tone="fund"
            icon={FileText}
            title="Ler o relatório do mês"
            description="Para onde foi o dinheiro: a alocação da carteira, as operações, as taxas e os rendimentos."
            alsoIn="Relatório"
            actionLabel="Abrir relatório"
            onAction={() => actions.goTo("report")}
          />
        )}
      </ActionGroup>
    </div>
  );
}
