import { ExpansionEmblem } from "@/shared/components/expansion-emblem";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Empty, EmptyDescription, EmptyHeader, EmptyTitle } from "@/shared/components/ui/empty";

/** Antes da primeira posse: o computador governa e os impostos ficam como estão. */
export function BeforeFirstTerm() {
  return (
    <Card>
      <CardContent>
        <Empty>
          <ExpansionEmblem expansion="government" size="lg" />
          <EmptyHeader>
            <EmptyTitle>O computador governa até a primeira posse</EmptyTitle>
            <EmptyDescription>
              Antes da posse ninguém propõe medidas e os impostos seguem como estão. Quem vencer a eleição passa a
              governar: propõe mudanças de imposto ao Congresso, acompanha a aprovação e, em troca, fica com a carteira
              congelada.
            </EmptyDescription>
          </EmptyHeader>
          <Badge variant="secondary">Governo do computador até a posse</Badge>
        </Empty>
      </CardContent>
    </Card>
  );
}
