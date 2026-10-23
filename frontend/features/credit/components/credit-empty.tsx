import { Lightbulb } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Empty, EmptyContent, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from "@/shared/components/ui/empty";
import { displayMoney, displayPercent } from "@/shared/lib/utils/display";
import type { CreditOverview } from "@/types";

type CreditEmptyProps = {
  overview: CreditOverview;
  onSimulate: () => void;
};

/** Primeiro acesso: ainda não há empréstimo, e o que a nota atual já libera. */
export function CreditEmpty({ overview, onSimulate }: CreditEmptyProps) {
  const { offer, rating } = overview;

  return (
    <Card>
      <CardContent>
        <Empty variant="dashed">
          <EmptyHeader>
            <EmptyMedia variant="icon">
              <Lightbulb />
            </EmptyMedia>
            <EmptyTitle>Você ainda não pegou crédito</EmptyTitle>
            <EmptyDescription>
              {offer.available && offer.annual_rate !== null ? (
                <>
                  Com a nota {rating.grade}, a dívida pode ir até{" "}
                  <b className="font-mono text-foreground">{displayMoney(offer.max_amount)}</b>, a{" "}
                  {displayPercent(offer.annual_rate)} ao ano.
                </>
              ) : (
                "Sem crédito novo com a nota atual."
              )}{" "}
              Sem parcelas, o histórico conta como em dia.
            </EmptyDescription>
          </EmptyHeader>
          {offer.available && (
            <EmptyContent>
              <Button onClick={onSimulate}>Simular um empréstimo</Button>
            </EmptyContent>
          )}
        </Empty>
      </CardContent>
    </Card>
  );
}
