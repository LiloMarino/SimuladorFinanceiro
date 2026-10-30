import { Megaphone, TriangleAlert } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from "@/shared/components/ui/empty";
import { Skeleton } from "@/shared/components/ui/skeleton";

/** Esqueleto do cartão das ações: o cabeçalho, as quatro ações e as linhas dos grupos. */
export function CampaignSkeleton() {
  return (
    <Card>
      <CardContent>
        <div className="grid gap-3" aria-busy="true" aria-label="Carregando as ações de campanha">
          <div className="grid gap-1.5">
            <h2 className="text-[15px] font-semibold">Ações de campanha</h2>
            <Skeleton className="h-3 w-3/5" />
          </div>
          <div className="grid gap-2.5 sm:grid-cols-2 xl:grid-cols-4">
            {Array.from({ length: 4 }, (_, index) => (
              <Skeleton key={index} className="h-32" />
            ))}
          </div>
          {Array.from({ length: 4 }, (_, index) => (
            <div key={index} className="flex items-center gap-2.5">
              <Skeleton className="size-7" />
              <Skeleton className="h-3 w-2/5" />
              <span className="flex-1" />
              <Skeleton className="h-3 w-15" />
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

/** Falha ao carregar só o cartão: o resto da página segue valendo. */
export function CampaignError({ onRetry }: { onRetry: () => void }) {
  return (
    <Card>
      <CardContent>
        <div className="grid gap-3">
          <h2 className="text-[15px] font-semibold">Ações de campanha</h2>
          <Alert variant="destructive">
            <TriangleAlert />
            <AlertTitle>Não deu para carregar as ações</AlertTitle>
            <AlertDescription>
              <div className="grid gap-2">
                <span>O resto da página continua valendo; só este cartão falhou.</span>
                <Button size="sm" variant="outline" className="w-fit" onClick={onRetry}>
                  Tentar de novo
                </Button>
              </div>
            </AlertDescription>
          </Alert>
        </div>
      </CardContent>
    </Card>
  );
}

type CampaignNotMemberProps = {
  /** Há partido de jogador para se filiar */
  canJoin: boolean;
  onJoin: () => void;
  onFound: () => void;
};

/** Quem não é filiado: as ações são dos filiados, e a pessoa acompanha pela pesquisa e pelo jornal. */
export function CampaignNotMember({ canJoin, onJoin, onFound }: CampaignNotMemberProps) {
  return (
    <Empty variant="dashed">
      <EmptyHeader>
        <EmptyMedia variant="icon">
          <Megaphone />
        </EmptyMedia>
        <EmptyTitle>Filie-se para fazer campanha</EmptyTitle>
        <EmptyDescription>
          As ações são dos filiados, pagas da própria carteira. Sem partido, você acompanha pela pesquisa e pelo jornal.
        </EmptyDescription>
      </EmptyHeader>
      <div className="flex gap-2">
        <Button variant="outline" size="sm" onClick={onFound}>
          Fundar um partido
        </Button>
        {canJoin && (
          <Button size="sm" onClick={onJoin}>
            Filiar-se
          </Button>
        )}
      </div>
    </Empty>
  );
}
