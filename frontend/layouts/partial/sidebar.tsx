import { NavLink } from "react-router-dom";
import type { NavItem } from "@/types";
import {
  Sidebar as SidebarRoot,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuBadge,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/shared/components/ui/sidebar";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { BrandMark } from "@/shared/components/brand-mark";
import { useAuth } from "@/shared/hooks/useAuth";
import { useDebugMode } from "@/shared/hooks/useDebugMode";
import { useSimulation } from "@/shared/hooks/useSimulation";
import { useRoomPlayers } from "@/shared/hooks/queries/useRoomPlayers";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { simulationSettingsOptions } from "@/shared/lib/queries/simulationSettingsOptions";

interface SidebarProps {
  navItems: NavItem[];
  activePage: string;
}

const NAV_GROUPS: NavItem["group"][] = ["Mercado", "Você", "Ferramentas"];

export default function Sidebar({ navItems, activePage }: SidebarProps) {
  const { user } = useAuth();
  const { simulation } = useSimulation();
  const { data: players } = useRoomPlayers();
  const { data: settings } = useApiQuery(simulationSettingsOptions());

  const debug = useDebugMode();

  // As ferramentas de diagnóstico medem o servidor do host: só ele as vê
  const showDebugTools = debug && !!settings?.is_host;
  const nickname = user?.nickname ?? "";
  const role = settings?.is_host ? "Host" : "Jogador";
  const playerCount = players?.length ?? 0;

  return (
    <SidebarRoot collapsible="none" className="h-svh">
      {/* Marca e partida */}
      <SidebarHeader>
        <BrandMark size="sm" />
        <div className="grid min-w-0">
          <span className="text-[15px] font-bold text-sidebar-accent-foreground">FinSim</span>
          <span className="truncate text-xs text-sidebar-muted">{simulation?.simulation?.name}</span>
        </div>
      </SidebarHeader>

      {/* Navegação por grupo */}
      <SidebarContent>
        {NAV_GROUPS.map((group) => (
          <SidebarGroup key={group}>
            <SidebarGroupLabel>{group}</SidebarGroupLabel>
            <SidebarMenu>
              {navItems
                .filter((item) => item.group === group && (!item.debugOnly || showDebugTools))
                .map((item) => (
                  <SidebarMenuItem key={item.key}>
                    <SidebarMenuButton isActive={activePage === item.key} render={<NavLink to={item.endpoint} />}>
                      <item.icon />
                      <span>{item.label}</span>
                    </SidebarMenuButton>
                    {item.badge && <SidebarMenuBadge tone={item.badgeTone}>{item.badge}</SidebarMenuBadge>}
                  </SidebarMenuItem>
                ))}
            </SidebarMenu>
          </SidebarGroup>
        ))}
      </SidebarContent>

      {/* Jogador */}
      <SidebarFooter>
        <PlayerAvatar nickname={nickname} color={players?.find((p) => p.nickname === nickname)?.color} />
        <div className="grid min-w-0">
          <span className="truncate font-semibold text-sidebar-accent-foreground">{nickname}</span>
          <span className="text-xs text-sidebar-muted">
            {role} · {playerCount} {playerCount === 1 ? "jogador" : "jogadores"}
          </span>
        </div>
      </SidebarFooter>
    </SidebarRoot>
  );
}
