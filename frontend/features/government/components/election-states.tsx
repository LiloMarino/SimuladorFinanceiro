import { ExpansionEmblem } from "@/shared/components/expansion-emblem";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Empty, EmptyDescription, EmptyHeader, EmptyTitle } from "@/shared/components/ui/empty";
import { displayShortDate } from "@/shared/lib/utils/display";
import type { ElectionPanel } from "@/types";
import { useToday } from "../hooks/useToday";
import { countdownLabel } from "../lib/election";

/** Antes de a campanha abrir, para quem não funda nem se filia: a página diz quando a eleição começa e quanto falta. */
export function BeforeCampaignEmpty({ panel }: { panel: ElectionPanel }) {
  const today = useToday(panel);
  return (
    <Card>
      <CardContent>
        <Empty>
          <ExpansionEmblem expansion="government" size="lg" />
          <EmptyHeader>
            <EmptyTitle>A campanha abre em {displayShortDate(panel.dates.campaign_start)}</EmptyTitle>
            <EmptyDescription>
              Um ano antes da eleição de {displayShortDate(panel.dates.first_round)}. Aí os partidos inscrevem as chapas
              e fazem campanha; até lá, o governo é do computador e não muda impostos.
            </EmptyDescription>
          </EmptyHeader>
          <Badge variant="secondary">Faltam {countdownLabel(today, panel.dates.campaign_start)}</Badge>
        </Empty>
      </CardContent>
    </Card>
  );
}
