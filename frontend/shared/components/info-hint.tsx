import type { ReactNode } from "react";
import { Info } from "lucide-react";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/shared/components/ui/tooltip";
import { Popover, PopoverContent, PopoverTrigger } from "@/shared/components/ui/popover";

interface InfoHintProps {
  children: ReactNode;
  label?: string;
  interactive?: boolean;
}

export function InfoHint({ children, label = "Como funciona", interactive = false }: InfoHintProps) {
  if (interactive)
    return (
      <Popover>
        <PopoverTrigger type="button" aria-label={label}>
          <Info className="size-4 text-muted-foreground" />
        </PopoverTrigger>
        <PopoverContent side="top" className="w-auto max-w-[min(90vw,32rem)]">
          <div className="text-xs">{children}</div>
        </PopoverContent>
      </Popover>
    );
  return (
    <Tooltip>
      <TooltipTrigger type="button" aria-label={label}>
        <Info className="size-4 text-muted-foreground" />
      </TooltipTrigger>
      <TooltipContent side="top" className="max-w-72">
        {children}
      </TooltipContent>
    </Tooltip>
  );
}
