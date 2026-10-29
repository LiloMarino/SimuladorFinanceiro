import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ListChecks } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { Popover, PopoverContent, PopoverTrigger } from "@/shared/components/ui/popover";
import { SidebarMenuBadge, SidebarMenuButton, SidebarMenuItem } from "@/shared/components/ui/sidebar";
import type { Pending } from "@/types";
import { usePending } from "../hooks/queries/usePending";
import { usePendingToasts } from "../hooks/usePendingToasts";
import { pendingTarget, severeCount, severeLabel } from "../lib/pending";
import { PendingRow } from "./pending-row";

/**
 * A linha Pendências no topo do menu lateral: mostra a contagem (vermelha se alguma é grave) e
 * abre a lista numa janela ao lado, sem pausar a partida. Sem pendência, a linha não existe.
 */
export function PendingMenuItem() {
  const { data: items } = usePending();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);

  const goTo = (item: Pending) => {
    const target = pendingTarget(item);
    setOpen(false);
    void navigate(target.to, { state: target.state });
  };

  usePendingToasts(items, goTo);

  if (!items || items.length === 0) return null;
  const severe = severeCount(items);

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <SidebarMenuItem>
        <PopoverTrigger render={<SidebarMenuButton isActive={open} />}>
          <ListChecks />
          <span>Pendências</span>
        </PopoverTrigger>
        <SidebarMenuBadge tone={severe > 0 ? "destructive" : "warning"}>{items.length}</SidebarMenuBadge>
      </SidebarMenuItem>
      <PopoverContent
        side="right"
        align="start"
        sideOffset={8}
        variant="flush"
        className="max-h-[calc(100svh-6rem)] w-80"
      >
        <div className="flex items-center gap-2 px-4 pt-3.5 pb-2.5">
          <b className="text-[15px] font-semibold">Pendências</b>
          {severe > 0 && (
            <Badge variant="destructive" className="ml-auto">
              {severeLabel(severe)}
            </Badge>
          )}
        </div>
        <ul>
          {items.map((item) => (
            <PendingRow key={item.key} item={item} onAct={goTo} />
          ))}
        </ul>
      </PopoverContent>
    </Popover>
  );
}
