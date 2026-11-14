import type { ReactNode } from "react";
import { Badge } from "@/shared/components/ui/badge";
import { EXPANSIONS, type ExpansionKey } from "@/shared/lib/expansions";
import { cn } from "@/shared/lib/utils";

type ExpansionIntroProps = {
  expansion: ExpansionKey;
  enabled: boolean;
  /** A chave liga/desliga da expansão */
  children: ReactNode;
};

/** O topo do cartão de uma expansão: faixa colorida, o que ela traz e a chave. */
export function ExpansionIntro({ expansion, enabled, children }: ExpansionIntroProps) {
  const { label, icon: Icon, description, highlights, bannerClass } = EXPANSIONS[expansion];
  return (
    <>
      {/* Faixa do cartão */}
      <div className={cn("relative flex h-28 items-end px-4 py-3.5", bannerClass)}>
        <span className="inline-flex size-14 items-center justify-center rounded-[14px] bg-white/15 text-white ring-1 ring-white/25 ring-inset">
          <Icon className="size-[30px]" />
        </span>
        <span className="ml-3 grid text-white">
          <b className="text-xl">{label}</b>
          <span className="text-xs opacity-80">Expansão</span>
        </span>
      </div>

      {/* O que a expansão traz e a chave */}
      <div className="grid gap-2.5 px-4 py-3.5">
        <span className="text-[13px]">{description}</span>
        <ul className="list-disc pl-[18px] text-xs leading-normal text-muted-foreground">
          {highlights.map((highlight) => (
            <li key={highlight} className="mb-1">
              {highlight}
            </li>
          ))}
        </ul>
        <div className="flex items-center justify-between gap-2.5">
          <Badge variant={enabled ? "info" : "secondary"}>{enabled ? "Ligada nesta partida" : "Desligada"}</Badge>
          {children}
        </div>
      </div>
    </>
  );
}
