import type { ReactNode } from "react";
import { Info, type LucideIcon } from "lucide-react";
import type { Popover as PopoverPrimitive } from "@base-ui/react/popover";
import { Popover, PopoverContent, PopoverTrigger } from "@/shared/components/ui/popover";

interface InfoHintProps {
  children: ReactNode;
  label?: string;
  /** A dica aceita seleção e links: o ponteiro pode entrar nela sem fechá-la */
  interactive?: boolean;
  /** O ícone que abre a dica; sem ele, o "i" de informação */
  icon?: LucideIcon;
}

// O clique no ícone só abre: fechar é sair do ícone, tocar fora ou Esc
const keepOpenOnTriggerPress: PopoverPrimitive.Root.Props["onOpenChange"] = (open, details) => {
  if (!open && details.reason === "trigger-press") details.cancel();
};

/** A dica abre ao passar o mouse, ao clicar e ao tocar; fora do ícone, ela fecha. */
export function InfoHint({ children, label = "Como funciona", interactive = false, icon: Icon = Info }: InfoHintProps) {
  return (
    <Popover onOpenChange={keepOpenOnTriggerPress}>
      <PopoverTrigger
        type="button"
        aria-label={label}
        openOnHover
        delay={interactive ? 100 : 0}
        closeDelay={interactive ? 200 : 0}
      >
        <Icon className="size-4 text-muted-foreground" />
      </PopoverTrigger>
      <PopoverContent side="top" className="w-auto max-w-[min(90vw,32rem)]">
        <div className="text-xs">{children}</div>
      </PopoverContent>
    </Popover>
  );
}
