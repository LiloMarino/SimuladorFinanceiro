import { CornerDownRight, Landmark, Lock, Plus, TriangleAlert } from "lucide-react";
import { Link } from "react-router-dom";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from "@/shared/components/ui/empty";
import { usePending } from "@/features/pending/hooks/queries/usePending";
import { displayDayMonth, displayMoney, displayQuantity } from "@/shared/lib/utils/display";
import type { FundRoomItem } from "@/types";
import { isHeldBy, managedHint, roomBlocks, roomLostFund, roomTotalNetWorth } from "../lib/fund-room";
import { FundRoomBlock } from "./fund-room-block";

type FundRoomListProps = { funds: FundRoomItem[]; userId: number };

/** A sala em três blocos (as que o jogador gere, as de que tem cotas e as outras); o botão de fundar aparece só a quem não tem gestora. */
export function FundRoomList({ funds, userId }: FundRoomListProps) {
  const { data: pending = [] } = usePending();
  const { managed, quotas, others } = roomBlocks(funds, userId);
  const holdsFund = funds.some((fund) => isHeldBy(fund, userId));
  const lost = roomLostFund(funds, userId);
  const found = (
    <Button variant="fund" nativeButton={false} render={<Link to="/funds/new" />}>
      <Plus />
      {lost ? "Fundar outra gestora" : "Fundar minha gestora"}
    </Button>
  );

  if (funds.length === 0) {
    return (
      <>
        <h1 className="text-2xl font-bold">Gestoras da sala</h1>
        {/* Sala sem gestora */}
        <Empty variant="dashed">
          <EmptyHeader>
            <EmptyMedia>
              <Landmark />
            </EmptyMedia>
            <EmptyTitle>Ninguém fundou uma gestora ainda</EmptyTitle>
            <EmptyDescription>
              A primeira a nascer aparece aqui e sai no jornal quando abrir a oferta pública.
            </EmptyDescription>
          </EmptyHeader>
          {found}
        </Empty>
      </>
    );
  }

  // A gestora congelada ou em licença volta ao jogador quando o mandato acaba
  const returning = managed.find(
    (fund) => (fund.frozen_until !== null && fund.manager_user_id === userId) || fund.leave_manager_user_id === userId,
  );
  const lostQuotas = lost ? Number(lost.my_quotas) : 0;

  return (
    <>
      {/* Cabeçalho */}
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div className="grid gap-1">
          <h1 className="text-2xl font-bold">Gestoras da sala</h1>
          <p className="text-[13px] text-muted-foreground">
            {holdsFund
              ? `${funds.length === 1 ? "1 gestora" : `${funds.length} gestoras`} · ${displayMoney(roomTotalNetWorth(funds))} de patrimônio somado`
              : lost
                ? "Você não gere nenhuma gestora agora."
                : "Você ainda não tem gestora."}
          </p>
        </div>
        {!holdsFund && found}
      </header>

      {/* A gestora que o jogador perdeu para a assembleia */}
      {lost && (
        <Alert variant="warning">
          <TriangleAlert />
          <AlertDescription>
            <b className="font-semibold">
              A assembleia da {lost.name} trocou o gestor
              {lost.manager_since ? ` em ${displayDayMonth(lost.manager_since)}` : ""}.
            </b>{" "}
            {lostQuotas > 0
              ? `Você segue com as suas ${displayQuantity(lost.my_quotas)} cotas, como cotista, e pode fundar outra gestora.`
              : "Você pode fundar outra gestora."}
          </AlertDescription>
        </Alert>
      )}

      {/* Você gere */}
      {managed.length > 0 && (
        <FundRoomBlock
          title="Você gere"
          hint={managedHint(managed, userId)}
          tone="fund"
          funds={managed}
          userId={userId}
          pending={pending}
          footer={
            <>
              {managed.length >= 2 && (
                <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
                  <CornerDownRight className="size-3 shrink-0" aria-hidden />
                  <span>
                    {managed.length === 2 ? "Junte as duas" : "Junte duas delas"} pela fusão, em{" "}
                    <b className="font-semibold text-foreground/70">Suas ações</b> de qualquer uma delas
                  </span>
                </p>
              )}
              {returning && (
                <Alert variant="muted">
                  <Lock />
                  <AlertDescription>
                    Fundar outra exige não ter gestora: a {returning.name} volta à sua mão quando o mandato acabar.
                  </AlertDescription>
                </Alert>
              )}
            </>
          }
        />
      )}

      {/* Você tem cotas */}
      {quotas.length > 0 && (
        <FundRoomBlock
          title="Você tem cotas"
          hint="Você vê a gestora como cotista: carteira, rendimentos, assembleia e relatório."
          tone="secondary"
          funds={quotas}
          userId={userId}
          pending={pending}
        />
      )}

      {/* Outras da sala */}
      {others.length > 0 && (
        <FundRoomBlock
          title="Outras da sala"
          hint="Cotas se compram na renda variável ou, durante a oferta, a preço fixo."
          tone="secondary"
          funds={others}
          userId={userId}
          pending={pending}
        />
      )}
    </>
  );
}
