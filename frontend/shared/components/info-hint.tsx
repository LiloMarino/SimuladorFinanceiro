import type { ReactNode } from "react";
import { Info } from "lucide-react";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/shared/components/ui/tooltip";

interface InfoHintProps {
  children: ReactNode;
  label?: string;
}

export function InfoHint({ children, label = "Como funciona" }: InfoHintProps) {
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <button type="button" className="text-muted-foreground" aria-label={label}>
          <Info className="size-4" />
        </button>
      </TooltipTrigger>
      <TooltipContent side="top" className="max-w-72">
        {children}
      </TooltipContent>
    </Tooltip>
  );
}
