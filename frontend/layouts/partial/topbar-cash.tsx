import { ChevronDown } from "lucide-react";
import type { ReactNode } from "react";
import { MetricHint } from "@/shared/components/metric-hint";
import { DropdownMenu, DropdownMenuTrigger } from "@/shared/components/ui/dropdown-menu";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { useGovernment } from "@/shared/hooks/queries/useGovernment";
import { useLifeStatus } from "@/shared/hooks/queries/useLifeStatus";
import { useSimulation } from "@/shared/hooks/useSimulation";
import { displayRatePercent } from "@/shared/lib/financial-independence";
import { OVERDRAFT } from "@/shared/lib/life-metrics";
import { cn } from "@/shared/lib/utils";
import { displayMoney, displaySignedMoney } from "@/shared/lib/utils/display";
import { AccountMenu } from "./account-menu";
import { FrozenLock } from "./frozen-lock";
import { useActiveAccount } from "./useActiveAccount";

type TopbarCashProps = {
  /** Caixa pessoal de hoje; indefinido antes do primeiro dado */
  cash: string | undefined;
  /** Só o viver de renda tem caixa negativo (cheque especial) */
  independence: boolean;
};

const LABEL = "flex items-center gap-1 text-xs font-semibold tracking-[.06em] uppercase";

/**
 * Caixa da conta em uso: a pessoal, ou a gestora escolhida no menu "Operar com".
 * No viver de renda, caixa pessoal negativo vira "Cheque especial" com o juro.
 */
export function TopbarCash({ cash, independence }: TopbarCashProps) {
  const { simulation } = useSimulation();
  const match = simulation?.simulation;
  const fundsEnabled = match?.funds_enabled === true;

  const { data: status } = useLifeStatus();
  const { accounts, active, switchAccount } = useActiveAccount();
  // Sem gestoras, o congelamento do presidente vem do painel do governo
  const { data: panel } = useGovernment({ enabled: match?.government_enabled === true && !fundsEnabled });

  const fund = active !== undefined && active.fund_id !== null;
  const shownCash = fund ? active.cash : cash;
  const overdraft = independence && !fund && cash !== undefined && Number(cash) < 0;
  const frozenUntil = fundsEnabled
    ? active?.frozen_until
    : panel?.is_president
      ? panel.portfolio?.frozen_until
      : undefined;
  const hasMenu = active !== undefined && (accounts?.length ?? 0) > 1;

  // O gatilho do menu é um botão: a dica de métrica (outro botão) só entra fora dele
  const lock = frozenUntil ? <FrozenLock until={frozenUntil} severalAccounts={fundsEnabled} /> : null;

  const content: ReactNode = overdraft ? (
    <>
      <span className={cn(LABEL, "text-destructive")}>
        {lock}
        {OVERDRAFT.label}
        {hasMenu ? <ChevronDown className="size-3.5 shrink-0" /> : <MetricHint metric={OVERDRAFT} />}
      </span>
      <span className="font-mono text-[15px] font-semibold text-destructive">{displaySignedMoney(cash)}</span>
      {status && (
        <span className="text-xs text-destructive">
          {displayRatePercent(status.overdraft_monthly_rate)} ao mês até cobrir
        </span>
      )}
    </>
  ) : (
    <>
      <span className={cn(LABEL, fund ? "text-fund" : "text-faint-foreground")}>
        {lock}
        <span className="max-w-40 truncate">Caixa · {fund ? active.name : "pessoal"}</span>
        {hasMenu && <ChevronDown className="size-3.5 shrink-0" />}
      </span>
      {shownCash !== undefined ? (
        <span className={cn("font-mono text-[15px] font-semibold", fund && "text-fund")}>
          {displayMoney(shownCash)}
        </span>
      ) : (
        <Skeleton className="h-4.5 w-30" />
      )}
    </>
  );

  const alignment = overdraft ? "justify-items-end" : "justify-items-start";

  if (!hasMenu || accounts === undefined) {
    return <div className={cn("grid border-l border-border pl-4", alignment)}>{content}</div>;
  }

  return (
    <div className="border-l border-border pl-2">
      <DropdownMenu>
        <DropdownMenuTrigger variant="block" className={alignment}>
          {content}
        </DropdownMenuTrigger>
        <AccountMenu accounts={accounts} active={active} onSelect={switchAccount} />
      </DropdownMenu>
    </div>
  );
}
