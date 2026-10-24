import { CalendarClock, Landmark } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from "@/shared/components/ui/empty";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { displayShortDate } from "@/shared/lib/utils/display";
import type { ElectionPanel } from "@/types";

/** Esqueleto no formato da tela: cabeçalho, pesquisa, tabela de partidos e a coluna lateral. */
export function ElectionSkeleton() {
  return (
    <div className="grid gap-5" aria-busy="true" aria-label="Carregando a eleição">
      <Skeleton className="h-44" />
      <div className="grid items-start gap-5 xl:grid-cols-[minmax(0,1fr)_380px]">
        <div className="grid gap-5">
          <Skeleton className="h-96" />
          <Skeleton className="h-64" />
        </div>
        <Skeleton className="h-96" />
      </div>
    </div>
  );
}

/** Antes de a candidatura abrir: a página diz quando a eleição começa. */
export function BeforeCampaignEmpty({ panel }: { panel: ElectionPanel }) {
  return (
    <Card>
      <CardContent>
        <Empty>
          <EmptyHeader>
            <EmptyMedia variant="icon">
              <CalendarClock />
            </EmptyMedia>
            <EmptyTitle>A candidatura abre em {displayShortDate(panel.dates.campaign_start)}</EmptyTitle>
            <EmptyDescription>
              Um ano antes do 1º turno, em {displayShortDate(panel.dates.first_round)}, abrem as inscrições: dá para fundar
              um partido, filiar-se, escolher a promessa e contribuir com a campanha. Até lá, o ranking de jogadores já
              vale.
            </EmptyDescription>
          </EmptyHeader>
        </Empty>
      </CardContent>
    </Card>
  );
}

type NoPartyBannerProps = {
  onJoin: () => void;
  onFound: () => void;
  canJoin: boolean;
};

/** Candidatura aberta e sem partido: o convite para se filiar ou fundar o próprio. */
export function NoPartyBanner({ onJoin, onFound, canJoin }: NoPartyBannerProps) {
  return (
    <Card>
      <CardContent>
        <div className="flex flex-wrap items-center gap-4">
          <span className="inline-flex size-10 items-center justify-center rounded-xl bg-info-soft text-primary">
            <Landmark className="size-5" />
          </span>
          <div className="grid min-w-0 flex-1 gap-0.5">
            <b className="text-[15px]">Você ainda não está em nenhum partido</b>
            <span className="text-[13px] text-muted-foreground">
              Só se concorre por partido. Filie-se a um dos abertos ou funde o seu; sozinho, é um partido de um filiado.
            </span>
          </div>
          <div className="flex gap-2">
            {canJoin && (
              <Button variant="outline" onClick={onJoin}>
                Filiar-se
              </Button>
            )}
            <Button onClick={onFound}>Fundar partido</Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
