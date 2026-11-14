import { Lock } from "lucide-react";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/shared/components/ui/tooltip";
import { frozenHint } from "./frozen-hint";

type FrozenLockProps = {
  /** Último dia do congelamento, "AAAA-MM-DD" */
  until: string;
  severalAccounts: boolean;
};

/** Cadeado da carteira congelada, com a dica ao passar o mouse. */
export function FrozenLock({ until, severalAccounts }: FrozenLockProps) {
  const { title, body } = frozenHint(until, severalAccounts);

  return (
    <Tooltip>
      <TooltipTrigger render={<span className="inline-flex cursor-help" />}>
        <Lock role="img" aria-label={title} className="size-3.5 text-warning" />
      </TooltipTrigger>
      <TooltipContent className="max-w-72 items-start">
        <span className="grid gap-0.5">
          <b className="font-semibold text-warning-soft">{title}</b>
          <span>{body}</span>
        </span>
      </TooltipContent>
    </Tooltip>
  );
}
