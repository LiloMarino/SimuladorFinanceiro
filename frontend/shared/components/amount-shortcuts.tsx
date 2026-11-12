import { cloneElement, useState, type ReactNode } from "react";
import { FieldDescription, FieldError } from "@/shared/components/ui/field";
import { Button } from "@/shared/components/ui/button";
import { Kbd } from "@/shared/components/ui/kbd";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/shared/components/ui/tooltip";
import { useHeldKey } from "@/shared/hooks/useHeldKey";
import { loadAmountMode, saveAmountMode, type AmountFieldKind } from "@/shared/lib/amount-mode-preference";
import {
  applyFixed,
  applyShare,
  clearedAmount,
  SHARES,
  visibleMode,
  type AmountMode,
} from "@/shared/lib/amount-shortcuts";
import { displayMoney, displayMoneyCompact } from "@/shared/lib/utils/display";
import { moneyToBody } from "@/shared/lib/utils/money-field";

type AmountShortcutsProps = {
  /** O tipo do campo: cada tipo lembra o próprio modo neste navegador */
  kind: AmountFieldKind;
  /** O modo de quem nunca trocou neste tipo de campo */
  defaultMode: AmountMode;
  /** O texto do campo: os atalhos em R$ somam a ele */
  value: string;
  /** `max` é verdadeiro quando o atalho pegou o total ("Tudo" ou "Máx") */
  onChange: (text: string, meta: { max: boolean }) => void;
  /** O valor em reais que vale 100% e o limite dos atalhos em R$; indefinido enquanto carrega */
  max: number | undefined;
  /** Da base da porcentagem: "do caixa", "da posição" */
  baseLabel: string;
  /** O limite pelo nome: "caixa", "posição" */
  limitLabel: string;
  /** Os três valores fixos do modo R$ */
  fixed: readonly [number, number, number];
  maxLabel?: string;
  disabled?: boolean;
  /** Erro do valor digitado à mão; ocupa o lugar da linha de baixo */
  error?: ReactNode;
  /** Complemento da linha de baixo (o que sobra, por exemplo) */
  note?: ReactNode;
};

/** A fila de atalhos de um campo de valor: o controle R$ | % e quatro botões que preenchem o campo. */
export function AmountShortcuts({
  kind,
  defaultMode,
  value,
  onChange,
  max,
  baseLabel,
  limitLabel,
  fixed,
  maxLabel = "Tudo",
  disabled,
  error,
  note,
}: AmountShortcutsProps) {
  const [saved, setSaved] = useState(() => loadAmountMode(kind, defaultMode));
  // O texto em que o último atalho em R$ parou no máximo; o aviso some quando o campo muda
  const [cappedAt, setCappedAt] = useState<string | null>(null);
  const shiftHeld = useHeldKey("Shift") && !disabled;
  const mode = visibleMode(saved, shiftHeld);

  const empty = max === 0;
  const percentUnavailable = max === undefined || empty;

  const changeSaved = (next: AmountMode) => {
    setSaved(next);
    saveAmountMode(kind, next);
  };

  const pickFixed = (amount: number) => {
    const result = applyFixed(value, amount, max);
    setCappedAt(result.capped ? result.text : null);
    onChange(result.text, { max: false });
  };

  const pickShare = (share: number) => {
    if (max === undefined) return;
    setCappedAt(null);
    onChange(applyShare(max, share), { max: share === 1 });
  };

  const other = saved === "money" ? "%" : "R$";

  return (
    <div className="grid gap-2">
      <div className="flex flex-wrap items-center gap-2">
        {/* Controle R$ | % e a tecla que mostra o outro modo */}
        <Tooltip>
          <TooltipTrigger render={<span />}>
            <span className="inline-flex items-center gap-1.5">
              <ToggleGroup
                variant="segmented"
                size="xs"
                aria-label="Modo dos atalhos"
                disabled={disabled}
                value={shiftHeld ? [] : [saved]}
                onValueChange={(values) => values[0] && changeSaved(values[0] as AmountMode)}
              >
                <ToggleGroupItem value="money" data-peek={(shiftHeld && mode === "money") || undefined}>
                  R$
                </ToggleGroupItem>
                <ToggleGroupItem value="percent" data-peek={(shiftHeld && mode === "percent") || undefined}>
                  %
                </ToggleGroupItem>
              </ToggleGroup>
              <Kbd className="ml-0" pressed={shiftHeld} aria-hidden>
                ⇧
              </Kbd>
            </span>
          </TooltipTrigger>
          <TooltipContent>
            <b className="font-semibold">⇧ Shift</b> Segure para usar os atalhos em {other} sem trocar o modo.
          </TooltipContent>
        </Tooltip>

        {/* Os quatro atalhos do modo que vale agora */}
        <div className="grid min-w-0 flex-1 basis-75 grid-cols-4 gap-1.5">
          {mode === "money" ? (
            <>
              {fixed.map((amount) => (
                <Button
                  key={amount}
                  type="button"
                  variant="outline"
                  size="sm"
                  disabled={disabled}
                  onClick={() => pickFixed(amount)}
                >
                  +{displayMoneyCompact(amount)}
                </Button>
              ))}
              <Button
                type="button"
                variant="outline"
                size="sm"
                disabled={disabled}
                onClick={() => {
                  setCappedAt(null);
                  onChange(clearedAmount(), { max: false });
                }}
              >
                Limpar
              </Button>
            </>
          ) : (
            SHARES.map((share) => (
              <ShareButton
                key={share}
                label={share === 1 ? maxLabel : `${share * 100}%`}
                hint={
                  max !== undefined && !empty
                    ? `${share * 100}% ${baseLabel}: ${displayMoney(moneyToBody(applyShare(max, share)))}`
                    : undefined
                }
                disabled={disabled || percentUnavailable}
                onClick={() => pickShare(share)}
              />
            ))
          )}
        </div>
      </div>

      {error ? (
        <FieldError>{error}</FieldError>
      ) : (
        <FieldDescription>
          {mode === "percent" ? (
            max === undefined ? (
              <Skeleton className="inline-block h-3 w-48 align-middle" />
            ) : empty ? (
              <>
                O máximo está em <span className="font-mono">{displayMoney(0)}</span>: não há do que tirar porcentagem.
              </>
            ) : (
              <>
                Porcentagem {baseLabel}: <span className="font-mono">{displayMoney(max)}</span>
              </>
            )
          ) : cappedAt !== null && cappedAt === value && max !== undefined ? (
            <span className="text-warning">
              Os atalhos pararam no máximo ({limitLabel}): <span className="font-mono">{displayMoney(max)}</span>
            </span>
          ) : (
            <>
              Os atalhos somam ao valor
              {max !== undefined && (
                <>
                  {" "}
                  · {limitLabel} <span className="font-mono">{displayMoney(max)}</span>
                </>
              )}
            </>
          )}
          {note}
        </FieldDescription>
      )}
    </div>
  );
}

type ShareButtonProps = { label: string; hint: string | undefined; disabled: boolean | undefined; onClick: () => void };

/** Um atalho de porcentagem; a dica diz em reais quanto ele vai preencher. */
function ShareButton({ label, hint, disabled, onClick }: ShareButtonProps) {
  const button = <Button type="button" variant="outline" size="sm" disabled={disabled} onClick={onClick} />;
  // Botão apagado não recebe ponteiro: sem dica
  if (!hint || disabled) return cloneElement(button, undefined, label);
  return (
    <Tooltip>
      <TooltipTrigger render={button}>{label}</TooltipTrigger>
      <TooltipContent>{hint}</TooltipContent>
    </Tooltip>
  );
}
