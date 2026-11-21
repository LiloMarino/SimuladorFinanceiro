import { Button } from "@/shared/components/ui/button";
import { QUANTITY_SHARES, shareLabel } from "@/shared/lib/quantity-shortcuts";
import { cn } from "@/shared/lib/utils";

type QuantityShortcutsProps = {
  /** Chamado com a fração do limite que o atalho representa (0,25, 0,5 ou 1) */
  onPick: (share: number) => void;
  /** O nome do atalho que pega o limite inteiro */
  maxLabel?: string;
  /** Apaga os atalhos enquanto o limite não é conhecido */
  disabled?: boolean;
  size?: "default" | "sm";
  className?: string;
};

/** A fila de atalhos de um campo de quantidade: 25%, 50% e o total do limite do campo. */
export function QuantityShortcuts({
  onPick,
  maxLabel = "Máx",
  disabled,
  size = "default",
  className,
}: QuantityShortcutsProps) {
  return (
    <div className={cn("flex shrink-0 gap-1.5", className)}>
      {QUANTITY_SHARES.map((share) => (
        <Button
          key={share}
          type="button"
          variant="outline"
          size={size}
          disabled={disabled}
          onClick={() => onPick(share)}
        >
          {shareLabel(share, maxLabel)}
        </Button>
      ))}
    </div>
  );
}
