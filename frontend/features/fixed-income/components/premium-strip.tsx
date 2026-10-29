import { Link } from "react-router-dom";
import { Landmark } from "lucide-react";
import { Card, CardContent } from "@/shared/components/ui/card";
import { cn } from "@/shared/lib/utils";
import { displayPercent } from "@/shared/lib/utils/display";
import type { Budget } from "@/types";
import { premiumSinceStart, signedPremium } from "../lib/premium";

type PremiumStripProps = { budget: Budget };

/** O prêmio de risco do governo hoje, quanto mudou desde o início e a porta para o orçamento. */
export function PremiumStrip({ budget }: PremiumStripProps) {
  const { month } = budget;
  const since = premiumSinceStart(budget);

  return (
    <Card>
      <CardContent>
        <div className="flex flex-wrap items-center gap-3.5">
          <span className="flex size-9 shrink-0 items-center justify-center rounded-[10px] bg-warning-soft text-warning">
            <Landmark className="size-[18px]" />
          </span>
          <div className="grid min-w-64 flex-1 gap-0.5">
            <b className="text-sm">
              Prêmio de risco do governo: {signedPremium(month.premium)} nos títulos novos do Tesouro
            </b>
            <span className="text-[13px] text-muted-foreground">
              A dívida está em {displayPercent(month.debt, 1)} do PIB; acima de{" "}
              {displayPercent(budget.premium_floor, 0)}, o Tesouro paga mais para tomar emprestado. O que você já tem na
              carteira mantém a taxa da compra.
            </span>
          </div>
          {since && (
            <span className={cn("font-mono text-[13px] whitespace-nowrap", since.rising && "text-warning")}>
              {since.text}
            </span>
          )}
          <Link
            to="/government?tab=accounts"
            className="text-[13px] font-medium whitespace-nowrap text-primary hover:underline"
          >
            Ver o orçamento ›
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}
