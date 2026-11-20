import { CalendarClock, Lock } from "lucide-react";
import type { ReactNode } from "react";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Spinner } from "@/shared/components/ui/spinner";
import { displayIsoDate, displayMoney, displayPercent } from "@/shared/lib/utils/display";
import type { FundDetails } from "@/types";
import { useLeaveComanagement } from "../hooks/mutations/useLeaveComanagement";
import { useFixedTeams } from "../hooks/useFixedTeams";
import { MAX_COMANAGERS } from "@/shared/lib/fund-comanager-shares";
import { hasScheduledChange, isInvited, splitMonthly, type Comanager } from "../lib/fund-comanagers";
import { FundSection } from "@/shared/components/fund-section";

type ManagerActions = {
  onInvite: () => void;
  onChangeShare: (comanager: Comanager) => void;
  onRemove: (comanager: Comanager) => void;
};

type FundManagersCardProps = {
  fund: FundDetails;
  /** As ações do gestor principal; sem elas o cartão só mostra quem gere */
  actions?: ManagerActions;
};

type RowProps = {
  nickname: string;
  color: string | null;
  caption: string;
  /** A parte das taxas em vigor (fração) */
  share: number;
  /** O que a parte rende por mês, em reais; nulo enquanto não há patrimônio */
  monthly: number | null;
  badge?: string;
  children?: ReactNode;
};

/** Uma linha do cartão: quem é, o papel, a parte das taxas e o que ela rende por mês. */
function ManagerRow({ nickname, color, caption, share, monthly, badge, children }: RowProps) {
  return (
    <li className="flex flex-wrap items-center gap-3 border-t border-muted py-2.5 first:border-t-0">
      <PlayerAvatar nickname={nickname} color={color ?? undefined} size="sm" />
      <div className="grid min-w-0 flex-1 gap-0.5">
        <span className="flex items-center gap-2 text-[13px] font-semibold">
          <span className="truncate">{nickname}</span>
          {badge && (
            <Badge variant="secondary" size="tag">
              {badge}
            </Badge>
          )}
        </span>
        <span className="text-xs text-muted-foreground">{caption}</span>
      </div>
      <div className="grid text-right">
        <b className="font-mono text-[13px] font-semibold">{displayPercent(share, 0)}</b>
        {monthly !== null && (
          <span className="font-mono text-xs text-muted-foreground">{displayMoney(monthly)}/mês</span>
        )}
      </div>
      {children}
    </li>
  );
}

/** Quem gere a gestora: o principal, os co-gestores que operam a carteira e os convites esperando resposta. */
export function FundManagersCard({ fund, actions }: FundManagersCardProps) {
  const leave = useLeaveComanagement(fund.id);
  const fixedTeams = useFixedTeams();
  const monthlyTotal = Number(fund.fees.management_monthly_estimate);
  const active = fund.comanagers.filter((comanager) => !isInvited(comanager));
  const invited = fund.comanagers.filter(isInvited);
  const comanagerMonthly = (comanager: Comanager) =>
    splitMonthly(monthlyTotal, Number(comanager.share) * 100).comanager;
  const managerMonthly = monthlyTotal - active.reduce((sum, comanager) => sum + comanagerMonthly(comanager), 0);
  const full = fund.comanagers.length >= MAX_COMANAGERS;
  const iAmComanager = fund.my_role === "comanager";

  return (
    <FundSection
      title="Gestores"
      action={
        actions &&
        !fixedTeams && (
          <Button size="xs" variant="outline" disabled={full} onClick={actions.onInvite}>
            Convidar co-gestor
          </Button>
        )
      }
    >
      <div className="grid gap-3">
        {fund.comanagers.length === 0 && actions && (
          <p className="text-[13px] text-muted-foreground">
            Você gere sozinho. Um co-gestor opera a carteira ao seu lado e divide as taxas com você, até{" "}
            {MAX_COMANAGERS} por gestora.
          </p>
        )}
        <ul className="grid">
          {/* Gestor principal */}
          <ManagerRow
            nickname={fund.manager_nickname ?? "—"}
            color={null}
            caption="Gestor principal"
            share={Number(fund.manager_share)}
            monthly={managerMonthly}
          />

          {/* Co-gestores que operam */}
          {active.map((comanager) => (
            <ManagerRow
              key={comanager.user_id}
              nickname={comanager.nickname}
              color={comanager.color}
              caption={comanager.since ? `Co-gestor desde ${displayIsoDate(comanager.since)}` : "Co-gestor"}
              share={Number(comanager.share)}
              monthly={comanagerMonthly(comanager)}
            >
              {actions && (
                <div className="flex gap-1.5">
                  <Button size="xs" variant="outline" onClick={() => actions.onChangeShare(comanager)}>
                    Mudar parte
                  </Button>
                  {!fixedTeams && (
                    <Button size="xs" variant="outline-destructive" onClick={() => actions.onRemove(comanager)}>
                      Remover
                    </Button>
                  )}
                </div>
              )}
              {hasScheduledChange(comanager) && comanager.pending_share !== null && comanager.pending_from !== null && (
                <p className="flex w-full items-center gap-1.5 text-xs text-info">
                  <CalendarClock className="size-3.5" />
                  Passa a {displayPercent(Number(comanager.pending_share), 0)} em{" "}
                  {displayIsoDate(comanager.pending_from)}
                </p>
              )}
            </ManagerRow>
          ))}

          {/* Convites pendentes */}
          {invited.map((comanager) => (
            <ManagerRow
              key={comanager.user_id}
              nickname={comanager.nickname}
              color={comanager.color}
              caption={
                comanager.expires_on ? `Convite até ${displayIsoDate(comanager.expires_on)}` : "Convite pendente"
              }
              share={Number(comanager.pending_share ?? 0)}
              monthly={null}
              badge="Pendente"
            >
              {actions && (
                <div className="flex gap-1.5">
                  <Button size="xs" variant="outline" onClick={() => actions.onChangeShare(comanager)}>
                    Mudar parte
                  </Button>
                  <Button size="xs" variant="outline-destructive" onClick={() => actions.onRemove(comanager)}>
                    Retirar
                  </Button>
                </div>
              )}
            </ManagerRow>
          ))}
        </ul>

        {fund.comanagers.length > 0 && (
          <Alert variant="info">
            <CalendarClock />
            <AlertDescription>
              A administração se divide a cada mês pelas partes acima, e a performance também. O convite pendente já
              reserva a parte dele, e a parte nova de quem já opera vale nas taxas do mês seguinte.
            </AlertDescription>
          </Alert>
        )}

        {/* Times fixos da aquisição hostil em equipes */}
        {fixedTeams && (
          <Alert variant="info">
            <Lock />
            <AlertDescription>
              Na aquisição hostil em equipes os co-gestores são os combinados no lobby: não há convite, saída nem
              remoção durante a partida.
            </AlertDescription>
          </Alert>
        )}

        {/* Saída do co-gestor */}
        {iAmComanager && !fixedTeams && (
          <div className="flex items-center justify-between gap-3">
            <p className="text-xs text-muted-foreground">
              Ao sair, o acesso à carteira da gestora acaba no mesmo pregão e a sua parte volta ao gestor principal.
            </p>
            <Button variant="outline-destructive" size="sm" disabled={leave.isPending} onClick={() => leave.mutate()}>
              {leave.isPending && <Spinner />}
              Sair da gestão
            </Button>
          </div>
        )}
      </div>
    </FundSection>
  );
}
