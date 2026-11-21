import { useQuery } from "@tanstack/react-query";
import { Bot, Hand } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { CardState } from "@/shared/components/card-state";
import { FundSection } from "@/shared/components/fund-section";
import { Button } from "@/shared/components/ui/button";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { accountStrategyQuery } from "@/shared/hooks/queries/useMyStrategy";
import { useStrategies } from "@/shared/hooks/queries/useStrategies";
import { useActiveAccount } from "@/shared/hooks/useActiveAccount";
import { displayDayMonth } from "@/shared/lib/utils/display";
import type { FundDetails } from "@/types";

const TITLE = "Automático da carteira";

/** O resumo do automático da gestora: qual estratégia opera e desde quando; ligar, ajustar e o registro ficam na página Estratégias. */
export function FundAutomaticSummary({ fund }: { fund: FundDetails }) {
  const mine = useQuery(accountStrategyQuery(fund.id));
  const strategies = useStrategies({ fund: true });
  const { switchAccount } = useActiveAccount();
  const navigate = useNavigate();

  if (!mine.data || !strategies.data) {
    return (
      <CardState
        title={TITLE}
        label="Carregando o automático da carteira"
        error={mine.error ?? strategies.error}
        onRetry={() => {
          void mine.refetch();
          void strategies.refetch();
        }}
        errorTitle="Não deu para carregar o automático"
      >
        <Skeleton className="h-10" />
      </CardState>
    );
  }

  const active = mine.data.active;
  const name = strategies.data.find((strategy) => strategy.key === active?.key)?.name;

  // A página Estratégias abre na conta da gestora
  const openStrategies = () => {
    switchAccount(fund.id);
    void navigate("/strategies");
  };

  return (
    <FundSection
      title={TITLE}
      action={
        <Button size="xs" variant="outline" onClick={openStrategies}>
          Abrir em Estratégias
        </Button>
      }
    >
      <div className="flex items-center gap-3">
        {active ? (
          <Bot className="size-5 shrink-0 text-success" />
        ) : (
          <Hand className="size-5 shrink-0 text-muted-foreground" />
        )}
        <div className="grid gap-0.5">
          <b className="text-sm font-semibold">
            {active ? `${name ?? "Uma estratégia"} opera a carteira` : "A carteira está no manual"}
          </b>
          <span className="text-[13px] text-muted-foreground">
            {active
              ? `Desde ${displayDayMonth(active.since)}. Os parâmetros e o registro das ordens ficam em Estratégias.`
              : "Ligue uma estratégia em Estratégias: a cada dia ela compra e vende pela gestora."}
          </span>
        </div>
      </div>
    </FundSection>
  );
}
