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
      <TooltipTrigger type="button" aria-label={label}>
        <Info className="size-4 text-muted-foreground" />
      </TooltipTrigger>
      <TooltipContent side="top" className="max-w-72">
        {children}
      </TooltipContent>
    </Tooltip>
  );
}
