import { Activity, CalendarCheck, HandCoins } from "lucide-react";
import type { ReactNode } from "react";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { displaySpread, displayWholePercent } from "@/shared/lib/credit";
import { displayMoneyCompact, displayPercent } from "@/shared/lib/utils/display";
import type { CreditOverview, CreditSuggestion } from "@/types";

type RatingSuggestionsCardProps = {
  overview: CreditOverview;
  /** Abre a amortização com o valor sugerido, em reais */
  onAmortize: (amount: string) => void;
};

/** "Como subir a nota": o caminho mais curto até a próxima faixa, uma sugestão por linha. */
export function RatingSuggestionsCard({ overview, onAmortize }: RatingSuggestionsCardProps) {
  const target = overview.suggestions.find((item) => item.target_grade !== null)?.target_grade ?? null;
  const description = target
    ? `O que leva você de ${overview.rating.grade} para ${target}, pelo caminho mais curto`
    : `Você está na nota ${overview.rating.grade}, a mais alta da escada`;

  const tierOf = (suggestion: CreditSuggestion) =>
    overview.rating.ladder.find((tier) => tier.grade === suggestion.target_grade);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Como subir a nota</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div>
          {overview.suggestions.map((suggestion) => {
            const tier = tierOf(suggestion);
            const reach =
              tier && tier.spread !== null
                ? `os próximos saem a SELIC ${displaySpread(tier.spread)} e o limite vai a ${displayWholePercent(tier.debt_limit)}`
                : null;

            if (suggestion.kind === "PAYOFF" || suggestion.kind === "RECOVER") {
              const amount = suggestion.amount ?? "0";
              return (
                <SuggestionRow
                  key={suggestion.kind}
                  icon={<HandCoins />}
                  title={`Quitar ${displayMoneyCompact(amount)}`}
                  action={
                    <Button variant="outline" size="xs" onClick={() => onAmortize(amount)}>
                      Amortizar
                    </Button>
                  }
                >
                  A alavancagem cai para {displayPercent(suggestion.leverage_after ?? 0, 0)} e a nota sobe para{" "}
                  {suggestion.target_grade}
                  {reach ? `: ${reach}.` : "."}
                </SuggestionRow>
              );
            }
            if (suggestion.kind === "VOLATILITY") {
              return (
                <SuggestionRow key={suggestion.kind} icon={<Activity />} title="Carteira mais calma">
                  Com a volatilidade em {displayPercent(suggestion.volatility ?? 0, 0)} ao ano, a nota também chega a{" "}
                  {suggestion.target_grade}.
                </SuggestionRow>
              );
            }
            return (
              <SuggestionRow key={suggestion.kind} icon={<CalendarCheck />} title="Seguir pagando em dia">
                Os 30 pontos de pagamento só caem com parcela atrasada.
              </SuggestionRow>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}

type SuggestionRowProps = {
  icon: ReactNode;
  title: string;
  action?: ReactNode;
  children: ReactNode;
};

function SuggestionRow({ icon, title, action, children }: SuggestionRowProps) {
  return (
    <div className="grid grid-cols-[auto_1fr_auto] items-start gap-x-3 gap-y-0.5 border-t border-muted py-3 first:border-t-0">
      <span className="row-span-2 flex size-8 items-center justify-center rounded-lg bg-info-soft text-primary [&_svg]:size-4">
        {icon}
      </span>
      <b className="font-semibold">{title}</b>
      <span className="row-span-2">{action}</span>
      <span className="text-[13px] text-muted-foreground">{children}</span>
    </div>
  );
}
