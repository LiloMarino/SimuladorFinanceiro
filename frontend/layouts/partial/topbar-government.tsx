import { ExpansionEmblem } from "@/shared/components/expansion-emblem";
import { Badge } from "@/shared/components/ui/badge";
import { useElection } from "@/shared/hooks/queries/useElection";

/** Selo do topo enquanto não há presidente empossado: o governo é do computador e não muda impostos. */
export function TopbarGovernment() {
  const { data: panel } = useElection();
  if (!panel || panel.term) return null;

  return (
    <Badge variant="secondary">
      <ExpansionEmblem expansion="government" size="xs" />
      Governo do computador até a posse
    </Badge>
  );
}
