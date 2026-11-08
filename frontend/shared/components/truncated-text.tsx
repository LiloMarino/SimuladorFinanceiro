import type { ReactNode } from "react";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/shared/components/ui/tooltip";
import { NAME_MAX_LENGTH } from "@/shared/lib/name-limit";
import { cn } from "@/shared/lib/utils";

type TruncatedTextProps = {
  children: ReactNode;
  className?: string;
  /** Corre dentro de uma frase (título de diálogo) e corta no tamanho de um nome. */
  inline?: boolean;
};

/** Texto de uma linha que termina em reticências e mostra o conteúdo inteiro no hover. */
export function TruncatedText({ children, className, inline }: TruncatedTextProps) {
  return (
    <Tooltip>
      {inline ? (
        <TooltipTrigger
          render={<span className="inline-block align-bottom" />}
          style={{ maxWidth: `${NAME_MAX_LENGTH}ch` }}
        >
          <span className={cn("block truncate", className)}>{children}</span>
        </TooltipTrigger>
      ) : (
        <TooltipTrigger render={<div className="min-w-0" />}>
          <span className={cn("block truncate", className)}>{children}</span>
        </TooltipTrigger>
      )}
      <TooltipContent side="top" className="max-w-64">
        {children}
      </TooltipContent>
    </Tooltip>
  );
}
