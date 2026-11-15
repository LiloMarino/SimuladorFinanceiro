import { Link } from "react-router-dom";
import { Card, CardContent } from "@/shared/components/ui/card";
import { displayDayMonth } from "@/shared/lib/utils/display";
import type { StateMovement } from "@/types";
import { movementText } from "../../lib/state-companies";

type StateMovementsCardProps = { movements: StateMovement[] };

/** Os fatos recentes das estatais, do mais novo ao mais antigo; cada um também sai como manchete no Jornal. */
export function StateMovementsCard({ movements }: StateMovementsCardProps) {
  return (
    <Card>
      <CardContent>
        <div className="grid min-w-0 content-start gap-3">
          {/* Header */}
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h2 className="text-[15px] font-semibold">Movimentos recentes</h2>
            <Link to="/journal" className="text-[13px] font-medium text-info hover:underline">
              Manchetes no Jornal ›
            </Link>
          </div>

          {/* Listagem de movimentos */}
          {movements.length === 0 ? (
            <p className="text-[13px] text-muted-foreground">
              Fundações, ordens e privatizações das estatais aparecem aqui.
            </p>
          ) : (
            <ul className="grid divide-y text-[13px]">
              {movements.map((movement) => (
                <li
                  key={`${movement.day}-${movement.kind}-${movement.ticker}-${movement.control}-${movement.dividend_policy}`}
                  className="flex items-baseline gap-3 py-2"
                >
                  <span className="w-14 shrink-0 font-mono text-xs text-muted-foreground">
                    {displayDayMonth(movement.day)}
                  </span>
                  <span>{movementText(movement)}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
