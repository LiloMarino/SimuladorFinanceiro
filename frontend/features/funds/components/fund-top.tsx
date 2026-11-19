import { Lock, Megaphone } from "lucide-react";
import { FundMark } from "@/shared/components/fund-mark";
import { CommonKpis } from "@/shared/components/fund-metrics-row";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Card } from "@/shared/components/ui/card";
import { fundStage, type FundStage } from "@/shared/lib/fund-view";
import { displayIsoDate, displayMoney, displayPercent, displayQuantity } from "@/shared/lib/utils/display";
import type { FundDetails } from "@/types";

const STAGE_LABEL: Record<FundStage, string> = { closed: "Fechada", offer: "Oferta aberta", listed: "Negociada" };

/** Quem gere, desde quando, o co-gestor e quantos cotistas há. */
function whoLine(fund: FundDetails, stage: FundStage): string {
  const manager = fund.my_role === "manager" ? "você" : (fund.manager_nickname ?? "—");
  const since = fund.manager_since ? ` desde ${displayIsoDate(fund.manager_since)}` : "";
  const parts = [`Gerida por ${manager}${since}`];

  if (stage === "closed") {
    parts.push("só o gestor tem cotas por enquanto");
  } else if (stage === "offer") {
    const buyers = fund.offer_buyers_count ?? fund.offer_buyers?.length ?? 0;
    parts.push(`${buyers} ${buyers === 1 ? "investidor" : "investidores"} na oferta`);
  } else {
    const active = fund.comanagers.filter((comanager) => comanager.status === "ACTIVE");
    parts.push(
      active.length > 0
        ? `${active.length === 1 ? "co-gestor(a)" : "co-gestores"}: ${active.map((comanager) => comanager.nickname).join(", ")}`
        : "sem co-gestor",
    );
    const holders = fund.holders.filter((holder) => holder.kind !== "maker").length;
    parts.push(`${holders} ${holders === 1 ? "cotista" : "cotistas"}`);
  }
  return parts.join(" · ");
}

/** O papel do jogador na gestora e o que ele tem nela. */
function RoleLine({ fund }: { fund: FundDetails }) {
  const mine = Number(fund.my_quotas);
  const total = Number(fund.quotas);
  const role =
    fund.my_role === "manager"
      ? { label: "Você é o gestor", variant: "fund" as const }
      : fund.my_role === "comanager"
        ? { label: "Você é co-gestor", variant: "info" as const }
        : mine > 0
          ? { label: "Você é cotista", variant: "info" as const }
          : { label: "Você não tem cotas", variant: "secondary" as const };

  return (
    <div className="flex flex-wrap items-center gap-2">
      <Badge variant={role.variant} size="tag">
        {role.label}
      </Badge>
      <span className="font-mono text-xs text-muted-foreground">
        {mine > 0
          ? `${displayQuantity(fund.my_quotas)} cotas · ${displayPercent(total > 0 ? mine / total : 0, 1)}`
          : "Compre na oferta ou no mercado"}
      </span>
    </div>
  );
}

/** O aviso da fase: a oferta em andamento ou a carteira congelada. */
function PhaseNotice({ fund, stage }: { fund: FundDetails; stage: FundStage }) {
  const frozen = fund.frozen_until && fund.my_role !== "viewer" ? fund.frozen_until : null;

  return (
    <>
      {stage === "offer" && (
        <Alert variant="info">
          <Megaphone />
          <AlertDescription>
            <b>Oferta pública aberta{fund.offer_ends_on ? ` até ${displayIsoDate(fund.offer_ends_on)}` : ""}</b>
            {fund.offer_price !== null && `, a ${displayMoney(fund.offer_price)} por cota`}:{" "}
            {displayQuantity(fund.offer_sold ?? "0")} cotas pedidas por{" "}
            {fund.offer_buyers_count ?? fund.offer_buyers?.length ?? 0} investidores até agora. A cota passa a ser
            negociada no mercado quando a oferta fecha.
          </AlertDescription>
        </Alert>
      )}
      {frozen && (
        <Alert variant="warning">
          <Lock />
          <AlertDescription>
            <b>Congelada até {displayIsoDate(frozen)}:</b> a gestora não opera, e as ordens da carteira dela ficam
            travadas até lá. Rendimentos, taxas, assembleia e o mercado da cota seguem normais.
          </AlertDescription>
        </Alert>
      )}
    </>
  );
}

/** O topo fixo da página da gestora: identidade, os quatro números comuns e o aviso da fase. */
export function FundTop({ fund }: { fund: FundDetails }) {
  const stage = fundStage(fund);

  return (
    <header className="grid gap-4">
      {/* Identidade */}
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="flex min-w-0 flex-1 items-start gap-3.5">
          <FundMark name={fund.name} size="lg" />
          <div className="grid min-w-0 gap-1.5">
            <h1 className="line-clamp-2 text-[22px] leading-tight font-bold break-words">{fund.name}</h1>
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant="fund" size="tag">
                <span className="font-mono">{fund.ticker}</span>
              </Badge>
              <Badge variant={stage === "closed" ? "secondary" : "success"} size="tag">
                {STAGE_LABEL[stage]}
              </Badge>
              {fund.frozen_until && (
                <Badge variant="warning" size="tag">
                  <Lock />
                  Congelada até {displayIsoDate(fund.frozen_until)}
                </Badge>
              )}
            </div>
            <p className="text-[13px] text-muted-foreground">{whoLine(fund, stage)}</p>
          </div>
        </div>
        <RoleLine fund={fund} />
      </div>

      {/* Os quatro números comuns */}
      <Card size="flush">
        <div className="grid grid-cols-2 xl:grid-cols-4">
          <CommonKpis fund={fund} cellClassName="px-4 py-3.5 nth-[2n]:border-l xl:not-first:border-l" />
        </div>
      </Card>

      {/* Aviso da fase */}
      <PhaseNotice fund={fund} stage={stage} />
    </header>
  );
}
