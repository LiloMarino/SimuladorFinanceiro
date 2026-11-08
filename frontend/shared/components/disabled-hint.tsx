import type { ReactNode } from "react";
import { cn } from "@/shared/lib/utils";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/shared/components/ui/tooltip";

type DisabledHintProps = {
  /** O motivo do botão estar desabilitado; `null` quando ele está liberado */
  reason: string | null;
  children: ReactNode;
  /** Classes do envoltório, para o botão ocupar a largura que ocuparia sozinho */
  className?: string;
};

/** Envolve o botão principal: enquanto houver `reason`, passar o mouse ou focar o botão mostra o motivo. */
export function DisabledHint({ reason, children, className }: DisabledHintProps) {
  if (!reason) return <>{children}</>;

  // O botão desabilitado não recebe ponteiro nem foco: o gatilho da dica é o envoltório, focável por teclado
  // oxlint-disable-next-line jsx-a11y/no-noninteractive-tabindex
  const trigger = <span className={cn("inline-flex", className)} tabIndex={0} />;

  return (
    <Tooltip>
      <TooltipTrigger render={trigger}>{children}</TooltipTrigger>
      <TooltipContent>{reason}</TooltipContent>
    </Tooltip>
  );
}
