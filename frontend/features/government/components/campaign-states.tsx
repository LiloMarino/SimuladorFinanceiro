import { Megaphone } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from "@/shared/components/ui/empty";

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
