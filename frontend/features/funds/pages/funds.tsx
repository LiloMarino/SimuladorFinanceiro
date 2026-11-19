import { CardState } from "@/shared/components/card-state";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { useAuth } from "@/shared/hooks/useAuth";
import usePageLabel from "@/shared/hooks/usePageLabel";
import { FundRoomList } from "../components/fund-room-list";
import { useFunds } from "../hooks/queries/useFunds";

/** As gestoras da sala em três blocos; quem não tem gestora vê o botão de fundar no topo. */
export default function FundsPage() {
  usePageLabel("Gestoras");
  const { user } = useAuth();
  const { data: funds, error, refetch } = useFunds();

  if (!funds || !user) {
    return (
      <CardState
        bare
        label="Carregando as gestoras"
        error={error}
        onRetry={() => void refetch()}
        errorTitle="Não deu para carregar as gestoras"
      >
        <Skeleton className="h-32" />
        <Skeleton className="h-72" />
      </CardState>
    );
  }

  return <FundRoomList funds={funds} userId={user.id} />;
}
