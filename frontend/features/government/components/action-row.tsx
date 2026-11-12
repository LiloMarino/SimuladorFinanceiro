import { CornerDownRight, Lock, type LucideIcon } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { cn } from "@/shared/lib/utils";

type ActionRowProps = {
  title: string;
  description: string;
  /** Onde a mesma ação também mora: "Contas › Impostos" */
  alsoIn: string;
  actionLabel: string;
  onAction: () => void;
  /** O ícone do grupo; a linha urgente do "Para decidir agora" vai sem ícone */
  icon?: LucideIcon;
  /** O número ou o prazo ao lado do título: "2 sem andar", "até 30 set" */
  chip?: string | undefined;
  /** A ação principal da tela ou a urgente leva o botão cheio */
  primary?: boolean;
  /** O motivo de a ação estar apagada, escrito à vista; com ele o botão não clica */
  blockedReason?: string | undefined;
};

/** Uma ação do jogador: o que faz, onde mais ela aparece e o botão que a abre ou leva até ela. */
export function ActionRow({
  title,
  description,
  alsoIn,
  actionLabel,
  onAction,
  icon: Icon,
  chip,
  primary = false,
  blockedReason,
}: ActionRowProps) {
  const blocked = blockedReason !== undefined;

  return (
    <div
      className={cn(
        "grid items-start gap-x-3.5 border-t px-5 py-3.5",
        Icon ? "grid-cols-[36px_minmax(0,1fr)_auto]" : "grid-cols-[minmax(0,1fr)_auto] items-center",
      )}
    >
      {Icon && (
        <span
          className={cn(
            "flex size-9 items-center justify-center rounded-[10px]",
            blocked ? "bg-muted text-muted-foreground" : "bg-primary/10 text-primary",
          )}
        >
          <Icon className="size-[18px]" />
        </span>
      )}
      <div className="grid min-w-0 gap-0.5">
        <div
          className={cn(
            "flex flex-wrap items-center gap-x-2 gap-y-1 text-sm font-semibold [overflow-wrap:anywhere]",
            blocked && "text-muted-foreground",
          )}
        >
          {title}
          {chip && (
            <Badge variant="warning" size="sm">
              {chip}
            </Badge>
          )}
        </div>
        <span className="text-[13px] text-muted-foreground [overflow-wrap:anywhere]">{description}</span>
        {blocked && (
          <span className="mt-1.5 inline-flex items-start gap-1.5 justify-self-start rounded-md bg-muted px-2.5 py-1 text-[13px] leading-[18px] text-foreground/80">
            <Lock className="mt-0.5 size-3.5 shrink-0" />
            {blockedReason}
          </span>
        )}
        <span className="mt-1 flex items-center gap-1.5 text-xs text-muted-foreground">
          <CornerDownRight className="size-3 shrink-0" />
          <span>
            Também em <b className="font-semibold text-foreground/70">{alsoIn}</b>
          </span>
        </span>
      </div>
      <Button
        size="sm"
        variant={primary && !blocked ? "default" : "outline"}
        disabled={blocked}
        onClick={onAction}
        className={Icon ? "mt-0.5" : undefined}
      >
        {actionLabel}
      </Button>
    </div>
  );
}
