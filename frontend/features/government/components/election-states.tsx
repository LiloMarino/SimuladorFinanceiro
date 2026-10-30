import { ExpansionEmblem } from "@/shared/components/expansion-emblem";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Empty, EmptyDescription, EmptyHeader, EmptyTitle } from "@/shared/components/ui/empty";
import { displayShortDate } from "@/shared/lib/utils/display";
import type { ElectionPanel } from "@/types";
import { useToday } from "../hooks/useToday";
import { countdownLabel } from "../lib/election";

/** Antes de a candidatura abrir: a página diz quando a eleição começa e quanto falta. */
export function BeforeCampaignEmpty({ panel }: { panel: ElectionPanel }) {
  const today = useToday(panel);
  return (
    <Card>
      <CardContent>
        <Empty>
          <ExpansionEmblem expansion="government" size="lg" />
          <EmptyHeader>
            <EmptyTitle>A candidatura abre em {displayShortDate(panel.dates.campaign_start)}</EmptyTitle>
            <EmptyDescription>
              Um ano antes da eleição de {displayShortDate(panel.dates.first_round)}. Aí dá para fundar um partido ou
              filiar-se a um; até lá, o governo é do computador e não muda impostos. Começar a campanha cedo rende mais
              votos por real gasto.
            </EmptyDescription>
          </EmptyHeader>
          <Badge variant="secondary">Faltam {countdownLabel(today, panel.dates.campaign_start)}</Badge>
        </Empty>
      </CardContent>
    </Card>
  );
}
