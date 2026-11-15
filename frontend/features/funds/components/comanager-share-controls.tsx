import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Slider } from "@/shared/components/ui/slider";
import { displayMoney } from "@/shared/lib/utils/display";
import { managerPointsAfter, splitMonthly } from "../lib/fund-comanagers";

type ComanagerShareControlsProps = {
  /** A parte do co-gestor na régua, em pontos percentuais inteiros */
  points: number;
  onChange: (points: number) => void;
  /** O que os outros co-gestores já reservam, em pontos */
  others: number;
  /** O teto da régua: sobra ao menos 1 ponto para o principal */
  max: number;
  /** O nome do co-gestor na frase do exemplo */
  nickname: string;
  /** O que a administração rende por mês, em média, em reais */
  monthly: number;
};

/** A régua da parte do co-gestor nas taxas e o exemplo em reais de quanto cada um recebe por mês. */
export function ComanagerShareControls({
  points,
  onChange,
  others,
  max,
  nickname,
  monthly,
}: ComanagerShareControlsProps) {
  const split = splitMonthly(monthly, points);
  const managerPoints = managerPointsAfter(others, points);

  return (
    <div className="grid gap-4">
      <div className="grid gap-2">
        <div className="flex items-baseline justify-between gap-3">
          <span className="text-sm font-medium">Parte do co-gestor nas taxas</span>
          <span className="font-mono text-[15px] font-semibold">{points}%</span>
        </div>
        <Slider
          aria-label="Parte do co-gestor nas taxas"
          min={1}
          max={max}
          step={1}
          value={points}
          onValueChange={onChange}
        />
        <div className="flex justify-between font-mono text-xs text-muted-foreground">
          <span>1%</span>
          <span>até {max}%</span>
        </div>
      </div>

      {/* Quem fica com quanto */}
      <div className="grid grid-cols-2 gap-2 rounded-lg bg-subtle px-3 py-2.5 text-[13px]">
        <span className="text-muted-foreground">Você, gestor principal</span>
        <b className="text-right font-mono font-semibold">{managerPoints}%</b>
        <span className="truncate text-muted-foreground">{nickname}</span>
        <b className="text-right font-mono font-semibold">{points}%</b>
        {others > 0 && (
          <>
            <span className="text-muted-foreground">Outros co-gestores</span>
            <b className="text-right font-mono font-semibold">{Math.round(others)}%</b>
          </>
        )}
      </div>

      <p className="rounded-lg bg-subtle px-3 py-2 text-xs text-muted-foreground">
        Com a administração rendendo {displayMoney(monthly)} por mês, {nickname} recebe{" "}
        <b className="font-mono font-semibold text-foreground">{displayMoney(split.comanager)}</b> e você fica com{" "}
        <b className="font-mono font-semibold text-foreground">{displayMoney(split.manager)}</b>. A performance se
        divide do mesmo jeito.
      </p>

      <Alert variant="info">
        <AlertTitle>A parte vale nas taxas do mês seguinte</AlertTitle>
        <AlertDescription>
          O co-gestor só opera a carteira da gestora: taxas, ofertas e emissões seguem com você.
        </AlertDescription>
      </Alert>
    </div>
  );
}
