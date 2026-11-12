import type { ReactNode } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Pin } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { TableCell, TableRow } from "@/shared/components/ui/table";
import { DailyLiquidityBadge } from "@/shared/components/daily-liquidity-badge";
import { InfoHint } from "@/shared/components/info-hint";
import { MetricHint } from "@/shared/components/metric-hint";
import { useEconomicIndicators } from "@/shared/hooks/queries/useEconomicIndicators";
import {
  displayDate,
  displayMoney,
  displayMonthName,
  displayPercent,
  displayRateLabel,
  parseLocalDate,
} from "@/shared/lib/utils/display";
import type { FixedIncomeOffer, PortfolioState } from "@/types";
import { breakEvenDollarRise } from "../lib/carry";
import { displayCap, isDollarAccount, isRareOffer } from "../lib/daily-liquidity";
import { BREAK_EVEN, DOLLAR_ACCOUNT_TAX, FED_RATE } from "../lib/dollar-account-metrics";
import { INVESTMENT_TYPE_LABELS, timeToMaturity } from "../lib/labels";

type OfferRowProps = {
  offer: FixedIncomeOffer;
  /** A posição do jogador no título; ausente quando ele não tem nada aplicado */
  position: PortfolioState["fixed_income"][number] | undefined;
  /** Com o filtro "Na carteira" ligado a linha mostra quanto está aplicado */
  showApplied: boolean;
  /** Com a taxa equivalente escondida (modo Especialista) a coluna "Equivale hoje" não existe */
  showRate: boolean;
  /** A maior taxa equivalente das linhas visíveis: dá o comprimento da barra */
  topRate: number;
  today: string | undefined;
};

/** Linha de uma oferta do mês. */
export function OfferRow({ offer, position, showApplied, showRate, topRate, today }: OfferRowProps) {
  return (
    <OfferRowShell offer={offer}>
      <TableCell>
        <div className="grid">
          <span className="flex items-center gap-2 font-semibold">
            <span className="max-w-[300px] truncate">{offer.name}</span>
            {position && <HeldBadge />}
          </span>
          {showApplied && <AppliedAmount position={position} />}
          <span className="max-w-[300px] truncate text-xs text-muted-foreground">
            {INVESTMENT_TYPE_LABELS[offer.investment_type]} · {offer.issuer}
          </span>
          {isRareOffer(offer) && offer.offered_until && offer.player_cap && (
            <span className="max-w-[300px] text-xs font-medium whitespace-normal text-warning">
              oferta do catálogo de {displayMonthName(offer.offered_until)} · até {displayCap(offer.player_cap)} por
              jogador
            </span>
          )}
        </div>
      </TableCell>
      <TableCell>
        <span className="font-mono">{displayRateLabel(offer.rate_index, offer.interest_rate)}</span>
      </TableCell>
      {showRate && (
        <TableCell>
          <EquivalentRate offer={offer} topRate={topRate} />
        </TableCell>
      )}
      <TableCell>
        <div className="grid">
          <span className="font-mono">{displayDate(parseLocalDate(offer.maturity_date))}</span>
          {today && <span className="text-xs text-muted-foreground">{timeToMaturity(offer.maturity_date, today)}</span>}
        </div>
      </TableCell>
      <TableCell>
        {offer.daily_liquidity ? (
          <DailyLiquidityBadge>Qualquer dia</DailyLiquidityBadge>
        ) : (
          <span className="text-[13px] text-muted-foreground">No vencimento</span>
        )}
      </TableCell>
      <TableCell>
        {offer.tax_exempt ? (
          <Badge variant="success">Isento</Badge>
        ) : (
          <Badge variant="secondary">22,5% → {displayPercent(offer.income_tax_rate_at_maturity, 1)}</Badge>
        )}
      </TableCell>
      <InvestCell offer={offer} />
    </OfferRowShell>
  );
}

/** Linha de uma oferta permanente (CDB de 100% do CDI ou conta em dólar), do grupo "Sempre disponíveis". */
export function PinnedOfferRow({ offer, position, showApplied, showRate, topRate }: Omit<OfferRowProps, "today">) {
  const { data: indicators } = useEconomicIndicators();
  const dollar = isDollarAccount(offer);
  // A conta em dólar leva o nome do tipo: o emissor não faz parte do título da linha
  const title = dollar ? INVESTMENT_TYPE_LABELS[offer.investment_type] : offer.name;
  const dollarToday = offer.fx_rate ? `US$ 1 = ${displayMoney(offer.fx_rate)}` : "—";
  const breakEven = indicators ? (
    <span className="flex items-center gap-1">
      empata se o dólar subir {displayPercent(breakEvenDollarRise(indicators.cdi, indicators.fed), 1)}
      <MetricHint metric={BREAK_EVEN} />
    </span>
  ) : null;

  return (
    <OfferRowShell offer={offer}>
      <TableCell>
        <div className="grid">
          <span className="flex items-center gap-1.5 font-semibold">
            <Pin className="size-3.5 shrink-0 text-faint-foreground" />
            <span className="max-w-[300px] truncate">{title}</span>
            {dollar && (
              <InfoHint label={`Como funciona ${title}`}>
                Rende o juro americano todo dia útil e volta ao caixa em qualquer pregão, pelo dólar do dia.
              </InfoHint>
            )}
            {position && <HeldBadge />}
          </span>
          {showApplied && (
            <span className="pl-5">
              <AppliedAmount position={position} />
            </span>
          )}
          <span className="max-w-[300px] truncate pl-5 text-xs text-muted-foreground">
            {dollar ? "Dólar · juro americano" : `${INVESTMENT_TYPE_LABELS[offer.investment_type]} · ${offer.issuer}`}
          </span>
        </div>
      </TableCell>
      <TableCell>
        {dollar ? (
          <div className="grid">
            <span className="font-mono">
              {indicators
                ? `${displayPercent(indicators.fed)} a.a. + dólar`
                : displayRateLabel(offer.rate_index, offer.interest_rate)}
            </span>
            <span className="flex items-center gap-1 text-xs text-muted-foreground">
              juro do Fed
              <MetricHint metric={FED_RATE} />
            </span>
            {!showRate && (
              <>
                <span className="text-xs text-muted-foreground">Dólar hoje {dollarToday}</span>
                <span className="text-xs text-muted-foreground">{breakEven}</span>
              </>
            )}
          </div>
        ) : (
          <span className="font-mono">{displayRateLabel(offer.rate_index, offer.interest_rate)}</span>
        )}
      </TableCell>
      {showRate && (
        <TableCell>
          {dollar ? (
            <div className="grid">
              <span className="font-mono font-semibold">{dollarToday}</span>
              <span className="text-xs text-muted-foreground">{breakEven}</span>
            </div>
          ) : (
            <EquivalentRate offer={offer} topRate={topRate} />
          )}
        </TableCell>
      )}
      <TableCell>
        <div className="grid">
          <span>Sem vencimento</span>
          <span className="text-xs text-muted-foreground">aberta a partida inteira</span>
        </div>
      </TableCell>
      <TableCell>
        <div className="grid">
          <div className="flex">
            <DailyLiquidityBadge>Qualquer dia</DailyLiquidityBadge>
          </div>
          <span className="text-xs text-muted-foreground">
            {dollar ? "pelo dólar do dia" : "volta ao caixa no pregão"}
          </span>
        </div>
      </TableCell>
      <TableCell>
        {dollar ? (
          <span className="inline-flex items-center gap-1.5">
            <Badge variant="secondary">15% do ganho</Badge>
            <MetricHint metric={DOLLAR_ACCOUNT_TAX} />
          </span>
        ) : (
          <Badge variant="secondary">22,5% → {displayPercent(offer.income_tax_rate_at_maturity, 1)}</Badge>
        )}
      </TableCell>
      <InvestCell offer={offer} />
    </OfferRowShell>
  );
}

function OfferRowShell({ offer, children }: { offer: FixedIncomeOffer; children: ReactNode }) {
  const navigate = useNavigate();
  return <TableRow onActivate={() => void navigate(`/fixed-income/${offer.asset_uuid}`)}>{children}</TableRow>;
}

function HeldBadge() {
  return (
    <Badge variant="info" size="sm">
      na carteira
    </Badge>
  );
}

function AppliedAmount({ position }: { position: OfferRowProps["position"] }) {
  return <span className="text-xs font-medium text-info">{displayMoney(position?.total_applied ?? 0)} aplicados</span>;
}

function EquivalentRate({ offer, topRate }: { offer: FixedIncomeOffer; topRate: number }) {
  return (
    <div className="flex items-center gap-2">
      <span className="h-1.5 w-14 overflow-hidden rounded-full bg-muted">
        <span
          className="block h-full rounded-full bg-success"
          style={{ width: `${(Number(offer.effective_annual_rate) / topRate) * 100}%` }}
        />
      </span>
      <span className="font-mono font-semibold">
        {offer.effective_annual_rate === null ? "—" : `${displayPercent(offer.effective_annual_rate)} a.a.`}
      </span>
    </div>
  );
}

function InvestCell({ offer }: { offer: FixedIncomeOffer }) {
  return (
    <TableCell>
      <Button
        variant="outline"
        size="sm"
        nativeButton={false}
        render={<Link to={`/fixed-income/${offer.asset_uuid}`} onClick={(e) => e.stopPropagation()} />}
      >
        Investir
      </Button>
    </TableCell>
  );
}
