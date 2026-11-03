import type { ReactNode } from "react";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/shared/components/ui/tooltip";
import { cn } from "@/shared/lib/utils";

type TruncatedTextProps = {
  children: ReactNode;
  className?: string;
};

/** Texto de uma linha que termina em reticências e mostra o conteúdo inteiro no hover. */
export function TruncatedText({ children, className }: TruncatedTextProps) {
  return (
    <Tooltip>
      <TooltipTrigger render={<div className="min-w-0" />}>
        <span className={cn("block truncate", className)}>{children}</span>
      </TooltipTrigger>
      <TooltipContent side="top" className="max-w-64">
        {children}
      </TooltipContent>
    </Tooltip>
  );
}
