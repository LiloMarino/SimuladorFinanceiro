import { Bot, EyeOff, Hand } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Separator } from "@/shared/components/ui/separator";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { displayDayMonth } from "@/shared/lib/utils/display";
import type { MyStrategy, StrategyInfo } from "@/types";
import { StrategyPanel } from "./strategy-panel";

export type Mode = "manual" | "automatic";

type ModeCardProps = {
  mine: MyStrategy;
  /** A estratégia ligada, com nome */
  activeStrategy: StrategyInfo | undefined;
  currentDate: string | undefined;
  onModeChange: (mode: Mode) => void;
};

/** Manual | Automático, com a estratégia que opera e o painel do que ela fez. */
export function ModeCard({ mine, activeStrategy, currentDate, onModeChange }: ModeCardProps) {
  const current: Mode = mine.active ? "automatic" : "manual";

  return (
    <Card>
      <CardContent>
        <div className="grid gap-4">
          <div className="flex flex-wrap items-center gap-5">
            <ToggleGroup
              variant="mode"
              size="mode"
              aria-label="Modo de jogo"
              value={[current]}
              onValueChange={(values) => values[0] && values[0] !== current && onModeChange(values[0] as Mode)}
            >
              <ToggleGroupItem value="manual">
                <Hand />
                Manual
              </ToggleGroupItem>
              <ToggleGroupItem value="automatic" tone="success">
                <Bot />
                Automático
              </ToggleGroupItem>
            </ToggleGroup>

            <div className="grid gap-1">
              {mine.active && activeStrategy ? (
                <>
                  <span className="flex flex-wrap items-center gap-2">
                    <b className="text-base font-semibold">{activeStrategy.name} opera por você</b>
                    <Badge variant="secondary" size="tag">
                      <EyeOff />
                      Só você vê
                    </Badge>
                  </span>
                  <span className="text-[13px] text-muted-foreground">
                    Desde {displayDayMonth(mine.active.since)}. As boletas ficam travadas: para operar à mão, volte ao
                    manual.
                  </span>
                </>
              ) : (
                <>
                  <b className="text-base font-semibold">Você joga no manual</b>
                  <span className="text-[13px] text-muted-foreground">
                    Escolha uma estratégia abaixo e ligue: a cada dia ela compra e vende por você.
                  </span>
                </>
              )}
            </div>
          </div>

          {mine.panel && (
            <>
              <Separator />
              <StrategyPanel panel={mine.panel} currentDate={currentDate} />
            </>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
