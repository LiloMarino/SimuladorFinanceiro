import type { ReactNode } from "react";
import { Info, type LucideIcon } from "lucide-react";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/shared/components/ui/tooltip";
import { Popover, PopoverContent, PopoverTrigger } from "@/shared/components/ui/popover";

interface InfoHintProps {
  children: ReactNode;
  label?: string;
  interactive?: boolean;
  /** O ícone que abre a dica; sem ele, o "i" de informação */
  icon?: LucideIcon;
}

export function InfoHint({ children, label = "Como funciona", interactive = false, icon: Icon = Info }: InfoHintProps) {
  if (interactive)
    return (
      <Popover>
        <PopoverTrigger type="button" aria-label={label}>
          <Icon className="size-4 text-muted-foreground" />
        </PopoverTrigger>
        <PopoverContent side="top" className="w-auto max-w-[min(90vw,32rem)]">
          <div className="text-xs">{children}</div>
        </PopoverContent>
      </Popover>
    );
  return (
    <Tooltip>
      <TooltipTrigger type="button" aria-label={label}>
        <Icon className="size-4 text-muted-foreground" />
      </TooltipTrigger>
      <TooltipContent side="top" className="max-w-72">
        {children}
      </TooltipContent>
    </Tooltip>
  );
}
