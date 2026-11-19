import { Clock } from "lucide-react";
import type { ReactNode } from "react";
import { Badge } from "@/shared/components/ui/badge";
import { Card } from "@/shared/components/ui/card";

type ActionGroupProps = {
  title: string;
  subtitle: string;
  /** O que fica à direita do título: o selo do que está bloqueado */
  aside?: ReactNode;
  children: ReactNode;
};

/** Um grupo de ações do mesmo papel: o título explica quem pode e as linhas vêm embaixo. */
export function ActionGroup({ title, subtitle, aside, children }: ActionGroupProps) {
  return (
    <Card size="flush" className="min-w-0">
      {/* Header */}
      <div className="flex items-start justify-between gap-3 px-5 py-4">
        <div className="grid min-w-0 gap-0.5">
          <h2 className="text-[15px] font-semibold [overflow-wrap:anywhere]">{title}</h2>
          <span className="text-[13px] text-muted-foreground [overflow-wrap:anywhere]">{subtitle}</span>
        </div>
        {aside}
      </div>
      {children}
    </Card>
  );
}

type DecideNowProps = { count: number; children: ReactNode };

/** O que tem prazo: passando dele, o jogo segue sem a decisão do jogador. */
export function DecideNow({ count, children }: DecideNowProps) {
  return (
    <Card variant="warning" size="flush" className="min-w-0">
      {/* Header */}
      <div className="flex flex-wrap items-center gap-x-2.5 gap-y-1 px-5 py-4">
        <Clock className="size-[18px] text-warning" />
        <h2 className="text-[15px] font-semibold">Para decidir agora</h2>
        <Badge variant="warning" size="sm" aria-label={`${count} decisões com prazo`}>
          {count}
        </Badge>
        <span className="ml-auto text-[13px] text-muted-foreground">
          Tem prazo: se passar, o jogo segue sem a sua decisão
        </span>
      </div>
      {children}
    </Card>
  );
}
