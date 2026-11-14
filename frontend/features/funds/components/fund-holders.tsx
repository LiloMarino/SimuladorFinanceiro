import { MetricLabel } from "@/shared/components/metric-hint";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { StackedBar } from "@/shared/components/stacked-bar";
import { playerColorStyle } from "@/shared/lib/player-colors";
import { displayPercent, displayQuantity } from "@/shared/lib/utils/display";
import type { FundDetails } from "@/types";
import { quotasToControl, sellableKeepingControl } from "../lib/fund-math";
import { CONTROL } from "../lib/fund-metrics";
import { FundSection } from "./fund-section";

type Holder = FundDetails["holders"][number];

// Cotista sem cor na paleta dos jogadores (bot e formador) fica no cinza do sistema
const NEUTRAL_FILL = "var(--faint-foreground)";

const fillOf = (holder: Holder) => (holder.color ? playerColorStyle(holder.color).background : NEUTRAL_FILL);

/** A barra das cotas por cotista, com a marca dos 50%, o limite do controle. */
function HoldersBar({ holders }: { holders: Holder[] }) {
  return (
    <div className="grid gap-1">
      <div className="relative">
        <StackedBar
          size="lg"
          segments={holders.map((holder) => ({
            key: `${holder.kind}-${holder.user_id ?? holder.nickname}`,
            fraction: Number(holder.share),
            fill: fillOf(holder),
          }))}
        />
        <span aria-hidden className="absolute -top-1 bottom-[-4px] left-1/2 w-0.5 bg-foreground" />
      </div>
      <div className="relative h-4 text-xs text-muted-foreground">
        <span className="absolute left-1/2 -translate-x-1/2 font-semibold text-foreground">50%</span>
      </div>
    </div>
  );
}

/** Quem tem as cotas, com a marca de 50% e a conta do controle: o gestor vê quanto pode vender, a sala vê quanto falta. */
export function FundHolders({ fund, viewer }: { fund: FundDetails; viewer: boolean }) {
  const total = Number(fund.quotas);
  const myQuotas = Number(fund.my_quotas);
  const managerQuotas = Number(fund.holders.find((holder) => holder.user_id === fund.manager_user_id)?.quotas ?? 0);
  const sellable = fund.sellable_keeping_control
    ? Number(fund.sellable_keeping_control)
    : sellableKeepingControl(managerQuotas, total);

  return (
    <FundSection title={<MetricLabel metric={CONTROL} />}>
      <div className="grid gap-3">
        <HoldersBar holders={fund.holders} />
        <ul className="grid">
          {fund.holders.map((holder) => (
            <li
              key={`${holder.kind}-${holder.user_id ?? holder.nickname}`}
              className="flex items-center gap-2.5 border-t border-muted py-2 text-[13px] first:border-t-0"
            >
              <PlayerAvatar
                nickname={holder.nickname}
                bot={holder.kind !== "player"}
                {...(holder.color ? { color: holder.color } : {})}
                size="sm"
              />
              <span className="min-w-0 flex-1 truncate font-medium" title={holder.nickname}>
                {holder.nickname}
                {holder.user_id === fund.manager_user_id && (
                  <span className="ml-1.5 text-xs font-normal text-muted-foreground">gestor</span>
                )}
              </span>
              <span className="font-mono text-muted-foreground">{displayQuantity(holder.quotas)}</span>
              <span className="w-14 text-right font-mono font-semibold">{displayPercent(holder.share, 1)}</span>
            </li>
          ))}
        </ul>
        {viewer ? (
          myQuotas > 0 && (
            <p className="rounded-lg bg-subtle px-3 py-2.5 text-xs text-muted-foreground">
              Você tem {displayQuantity(fund.my_quotas)} cotas.{" "}
              {quotasToControl(myQuotas, total) > 0
                ? `Faltam ${displayQuantity(String(quotasToControl(myQuotas, total)))} cotas para você chegar lá, aos 50%.`
                : "Você já passa dos 50%."}
            </p>
          )
        ) : (
          <p className="rounded-lg bg-subtle px-3 py-2.5 text-[13px]">
            Você pode vender até <b className="font-mono font-semibold">{displayQuantity(String(sellable))}</b> cotas
            sem perder o controle.
          </p>
        )}
      </div>
    </FundSection>
  );
}
