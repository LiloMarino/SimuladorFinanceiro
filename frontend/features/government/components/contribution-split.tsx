import { Info } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Slider } from "@/shared/components/ui/slider";
import { displayMoney } from "@/shared/lib/utils/display";

const SHORTCUTS = [0, 40, 50, 100];

type ContributionSplitProps = {
  /** Fatia do Congresso, de 0 a 100 */
  share: number;
  onShare: (share: number) => void;
  /** Contribuição mensal digitada, em reais */
  monthly: number;
  /** Sem chapa na presidência, a divisão some e tudo vai ao Congresso */
  runs: boolean;
};

/** "Para onde vai": a divisão da contribuição entre a presidência e o Congresso. */
export function ContributionSplit({ share, onShare, monthly, runs }: ContributionSplitProps) {
  if (!runs) {
    return (
      <div className="grid gap-2">
        <Alert variant="muted">
          <Info />
          <AlertTitle>O partido não lançou chapa</AlertTitle>
          <AlertDescription>
            Sem candidato à presidência, toda a contribuição vai para a campanha do Congresso, e a divisão some.
          </AlertDescription>
        </Alert>
        <div className="flex items-center justify-between text-[13px]">
          <span>Congresso · bancada</span>
          <b className="tabular-nums">{displayMoney(monthly)} · 100%</b>
        </div>
      </div>
    );
  }

  const congress = (monthly * share) / 100;
  return (
    <div className="grid gap-2.5">
      <span className="text-sm font-medium">Para onde vai</span>
      <div className="flex justify-between text-[13px]">
        <span>
          <b>Presidência</b> <span className="text-muted-foreground">{100 - share}%</span>
        </span>
        <span>
          <span className="text-muted-foreground">{share}%</span> <b>Congresso</b>
        </span>
      </div>
      <Slider
        value={100 - share}
        onValueChange={(value) => onShare(100 - value)}
        min={0}
        max={100}
        step={5}
        aria-label="Parte para a presidência"
      />
      <div className="flex flex-wrap gap-1.5">
        {SHORTCUTS.map((option) => (
          <Button
            key={option}
            type="button"
            size="xs"
            variant={share === option ? "info" : "outline"}
            onClick={() => onShare(option)}
          >
            {100 - option}/{option}
          </Button>
        ))}
      </div>
      <div className="grid grid-cols-2 gap-2.5">
        <SplitTile label="Presidência · candidato" amount={monthly - congress} />
        <SplitTile label="Congresso · bancada" amount={congress} />
      </div>
      <p className="rounded-lg bg-subtle px-2.5 py-2 text-xs leading-normal text-muted-foreground">
        A verba da presidência vira apoio para o candidato; a do Congresso, apoio para a bancada do partido.
      </p>
    </div>
  );
}

function SplitTile({ label, amount }: { label: string; amount: number }) {
  return (
    <div className="grid gap-1 rounded-lg border px-3 py-2.5">
      <span className="text-xs text-muted-foreground">{label}</span>
      <b className="text-lg tabular-nums">{displayMoney(amount)}</b>
    </div>
  );
}
