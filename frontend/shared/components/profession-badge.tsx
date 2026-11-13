import { Badge } from "@/shared/components/ui/badge";
import { PROFESSIONS } from "@/shared/lib/professions";
import type { Profession } from "@/types";

/** A profissão do jogador como chip; sem profissão (salário igual), nada. */
export function ProfessionBadge({ profession }: { profession: Profession | null | undefined }) {
  if (!profession) return null;
  const { name, icon: Icon } = PROFESSIONS[profession];
  return (
    <Badge variant="label" size="sm" className="shrink-0">
      <Icon />
      {name}
    </Badge>
  );
}
