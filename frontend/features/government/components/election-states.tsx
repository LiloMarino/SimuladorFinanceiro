import { RefreshCw, TriangleAlert } from "lucide-react";
import { ExpansionEmblem } from "@/shared/components/expansion-emblem";
import { Alert, AlertAction, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Empty, EmptyDescription, EmptyHeader, EmptyTitle } from "@/shared/components/ui/empty";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { displayShortDate } from "@/shared/lib/utils/display";
import type { ElectionPanel } from "@/types";
import { useToday } from "../hooks/useToday";
import { countdownLabel } from "../lib/election";

/** Esqueleto no formato da tela: cabeçalho, pesquisa, tabela de partidos e a coluna lateral. */
export function ElectionSkeleton() {
  return (
    <div className="grid gap-5" aria-busy="true" aria-label="Carregando a eleição">
      <Skeleton className="h-44" />
      <div className="grid items-start gap-5 xl:grid-cols-[minmax(0,1fr)_380px]">
        <div className="grid gap-5">
          <Card>
            <CardContent>
              <div className="grid gap-3">
                <Skeleton className="h-3.5 w-2/5" />
                <Skeleton className="h-50" />
                <Skeleton className="h-3 w-[70%]" />
              </div>
            </CardContent>
          </Card>
          <Skeleton className="h-64" />
        </div>
        <Skeleton className="h-96" />
      </div>
    </div>
  );
}

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

/** Falha ao carregar a eleição: o que houve, com a ação de tentar de novo ao lado. */
export function ElectionError({ onRetry }: { onRetry: () => void }) {
  return (
    <Card>
      <CardContent>
        <Alert variant="destructive">
          <TriangleAlert />
          <AlertTitle>Não deu para carregar a eleição</AlertTitle>
          <AlertDescription>
            A conexão com a partida caiu. Partidos, contribuições e votos seguem valendo; nada mudou fora da data.
          </AlertDescription>
          <AlertAction>
            <Button size="xs" variant="outline" onClick={onRetry}>
              <RefreshCw />
              Tentar de novo
            </Button>
          </AlertAction>
        </Alert>
      </CardContent>
    </Card>
  );
}
