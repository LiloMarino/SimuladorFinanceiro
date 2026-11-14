import { Lock } from "lucide-react";
import type { ReactNode } from "react";
import { FundMark } from "@/shared/components/fund-mark";
import { Badge } from "@/shared/components/ui/badge";
import { displayIsoDate } from "@/shared/lib/utils/display";
import type { FundDetails } from "@/types";
import { fundStage } from "../lib/fund-view";

type FundHeaderProps = {
  fund: FundDetails;
  /** A linha embaixo do nome: quem gere, quanto controla */
  subtitle: ReactNode;
  /** Os botões à direita */
  actions?: ReactNode;
  /** A faixa embaixo do cabeçalho, como "Você tem X%" */
  footer?: ReactNode;
};

const STAGE_LABEL = { closed: "Fechada", offer: "Oferta aberta", listed: "Negociada" } as const;

/** O cabeçalho da página da gestora: selo, nome (até 2 linhas), sigla embaixo, etapa e ações. */
export function FundHeader({ fund, subtitle, actions, footer }: FundHeaderProps) {
  const stage = fundStage(fund);

  return (
    <header className="grid gap-3">
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
            <p className="text-[13px] text-muted-foreground">{subtitle}</p>
          </div>
        </div>
        {actions && <div className="flex flex-wrap items-center gap-2">{actions}</div>}
      </div>
      {footer}
    </header>
  );
}
