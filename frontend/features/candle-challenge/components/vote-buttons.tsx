import { Button } from "@/shared/components/ui/button";
import type { ChallengeDirection } from "@/types";

interface VoteButtonsProps {
  /** O lado já escolhido: o botão fica cheio, e dá para trocar até a pergunta fechar. */
  direction: ChallengeDirection | null;
  disabled: boolean;
  onVote: (direction: ChallengeDirection) => void;
  compact?: boolean;
}

/** Sobe e Desce, com as teclas ↑ e ↓ (quem escuta o teclado é a janela). */
export function VoteButtons({ direction, disabled, onVote, compact = false }: VoteButtonsProps) {
  const size = compact ? "sm" : "xl";
  const height = compact ? undefined : "h-14";
  return (
    <div className="flex gap-3">
      <Button
        size={size}
        className={`flex-1 ${height ?? ""}`}
        variant={direction === "up" ? "success" : "outline-success"}
        aria-pressed={direction === "up"}
        disabled={disabled}
        onClick={() => onVote("up")}
      >
        ▲ Sobe
        {!compact && <Key>↑</Key>}
      </Button>
      <Button
        size={size}
        className={`flex-1 ${height ?? ""}`}
        variant={direction === "down" ? "destructive" : "outline-destructive"}
        aria-pressed={direction === "down"}
        disabled={disabled}
        onClick={() => onVote("down")}
      >
        ▼ Desce
        {!compact && <Key>↓</Key>}
      </Button>
    </div>
  );
}

function Key({ children }: { children: string }) {
  return (
    <kbd className="rounded border border-current/30 px-1.5 font-mono text-xs font-normal opacity-70">{children}</kbd>
  );
}
