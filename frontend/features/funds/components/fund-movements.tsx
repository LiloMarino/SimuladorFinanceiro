import { displayShortDate } from "@/shared/lib/utils/display";
import type { FundDetails } from "@/types";
import { movementText } from "../lib/fund-movements";
import { FundSection } from "./fund-section";

/** O que aconteceu na gestora, do mais recente ao mais antigo. */
export function FundMovements({ movements }: { movements: FundDetails["movements"] }) {
  return (
    <FundSection title="Movimentos">
      {movements.length === 0 ? (
        <p className="text-[13px] text-muted-foreground">Nada aconteceu ainda: os movimentos aparecem aqui.</p>
      ) : (
        <ul className="grid">
          {movements.map((movement, index) => (
            <li
              key={`${movement.day}-${movement.type}-${index}`}
              className="grid grid-cols-[6rem_1fr] gap-3 border-t border-muted py-2 text-[13px] first:border-t-0"
            >
              <span className="font-mono text-xs text-muted-foreground">{displayShortDate(movement.day)}</span>
              <span>{movementText(movement)}</span>
            </li>
          ))}
        </ul>
      )}
    </FundSection>
  );
}
