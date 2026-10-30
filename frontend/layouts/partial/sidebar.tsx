import { NavLink } from "react-router-dom";
import { Calculator } from "lucide-react";
import type { NavItem } from "@/types";
import { Badge } from "@/shared/components/ui/badge";
import { summarizeAssistances } from "@/shared/lib/assistance";
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
import { useDebugMode } from "@/shared/hooks/queries/useDebugMode";
import { useSimulation } from "@/shared/hooks/useSimulation";
import { useRoomPlayers } from "@/shared/hooks/queries/useRoomPlayers";
import { useMyStrategy } from "@/shared/hooks/queries/useMyStrategy";
import { useAchievementTally } from "@/shared/hooks/queries/useAchievementTally";
import { usePortfolio } from "@/shared/hooks/queries/usePortfolio";
import { useGoalProgress } from "@/shared/hooks/queries/useGoalProgress";
import { displayGoalPercent, ownStanding } from "@/shared/lib/goal";
import { useSimulationSettings } from "@/shared/hooks/queries/useSimulationSettings";
import { hasGoal } from "@/shared/lib/game-types";
import { TutorialMenuItem } from "@/features/tutorial/components/menu-item";
import { PendingMenuItem } from "@/features/pending/components/pending-menu-item";
import { PendingDot } from "@/features/pending/components/pending-dot";
import { usePending } from "@/features/pending/hooks/queries/usePending";
import { menuDotSeverity } from "@/features/pending/lib/pending";

interface SidebarProps {
  navItems: NavItem[];
  activePage: string;
}

const NAV_GROUPS: NavItem["group"][] = ["Mercado", "Você", "Expansões", "Ferramentas"];

export default function Sidebar({ navItems, activePage }: SidebarProps) {
  const { user } = useAuth();
  const { simulation } = useSimulation();
  const { data: players } = useRoomPlayers();
  const { data: settings } = useSimulationSettings();
  const { data: goal } = useGoalProgress();
  const tally = useAchievementTally();
  const { data: portfolio } = usePortfolio();
  const { data: myStrategy } = useMyStrategy();
  const { data: pending } = usePending();

  const debug = useDebugMode();

  // As ferramentas de diagnóstico medem o servidor do host: só ele as vê
  const showDebugTools = debug && !!settings?.is_host;
  const nickname = user?.nickname ?? "";
  const role = settings?.is_host ? "Host" : "Jogador";
  const playerCount = players?.length ?? 0;
  const match = simulation?.simulation;
  const racing = !!match && hasGoal(match.game_type);
  const governmentOn = !!match?.government_enabled;
  const isVisible = (item: NavItem) =>
    (!item.debugOnly || showDebugTools) && (!item.goalOnly || racing) && (!item.expansion || governmentOn);
  const isExpert =
    !!match &&
    summarizeAssistances([match.show_equivalent_rate, match.show_maturity_projection, match.show_chart_hints]).mode ===
      "EXPERT";
  const ownGoal = goal && match ? ownStanding(goal, match.player_grouping, nickname) : undefined;

  return (
    <SidebarRoot collapsible="none" className="h-svh">
      {/* Marca e partida */}
      <SidebarHeader>
        <BrandMark size="sm" />
        <div className="grid min-w-0">
          <span className="text-[15px] font-bold text-sidebar-accent-foreground">FinSim</span>
          <span className="truncate text-xs text-sidebar-muted">{simulation?.simulation?.name}</span>
          {isExpert && (
            <Badge variant="sidebar" size="tag" className="mt-1">
              <Calculator />
              Especialista
            </Badge>
          )}
        </div>
      </SidebarHeader>

      {/* Navegação por grupo */}
      <SidebarContent>
        {/* Pendências da partida */}
        <SidebarGroup>
          <SidebarMenu>
            <PendingMenuItem items={pending} />
          </SidebarMenu>
        </SidebarGroup>
        {NAV_GROUPS.filter((group) => navItems.some((item) => item.group === group && isVisible(item))).map((group) => (
          <SidebarGroup key={group}>
            <SidebarGroupLabel>{group}</SidebarGroupLabel>
            <SidebarMenu>
              {navItems
                .filter((item) => item.group === group && isVisible(item))
                .map((item) => {
                  const dot = item.pendingTypes ? menuDotSeverity(pending, item.pendingTypes) : undefined;
                  return item.tutorial ? (
                    <TutorialMenuItem key={item.key} label={item.label} icon={item.icon} />
                  ) : (
                    <SidebarMenuItem key={item.key}>
                      <SidebarMenuButton isActive={activePage === item.key} render={<NavLink to={item.endpoint} />}>
                        <item.icon />
                        <span>{item.label}</span>
                      </SidebarMenuButton>
                      {item.badge && <SidebarMenuBadge tone={item.badgeTone}>{item.badge}</SidebarMenuBadge>}
                      {item.goalOnly && ownGoal && (
                        <SidebarMenuBadge>{displayGoalPercent(ownGoal.fraction)}</SidebarMenuBadge>
                      )}
                      {item.creditAlert && portfolio?.credit_alert && (
                        <SidebarMenuBadge>
                          <span
                            aria-label="Parcela de crédito pedindo atenção"
                            className="size-2 rounded-full bg-destructive ring-2 ring-sidebar"
                          />
                        </SidebarMenuBadge>
                      )}
                      {dot && !item.strategyStatus && (
                        <SidebarMenuBadge>
                          <PendingDot severity={dot} label="Pendência pedindo atenção" />
                        </SidebarMenuBadge>
                      )}
                      {item.strategyStatus && myStrategy && (
                        <SidebarMenuBadge tone="plain">
                          {myStrategy.active ? (
                            <span className="inline-flex items-center gap-1.5 text-toast-success">
                              <span className="size-2 rounded-full bg-toast-success" />
                              Ligada
                            </span>
                          ) : dot ? (
                            <span className="inline-flex items-center gap-1.5 text-toast-warning">
                              Desligada
                              <PendingDot severity={dot} label="A estratégia deu erro" />
                            </span>
                          ) : (
                            <span className="text-sidebar-muted">Desligada</span>
                          )}
                        </SidebarMenuBadge>
                      )}
                      {item.achievementTally && tally && (
                        <SidebarMenuBadge>
                          <span className="inline-flex items-center gap-1.5">
                            {tally.hasNew && activePage !== item.key && (
                              <span aria-label="Conquista nova" className="size-1.5 rounded-full bg-toast-warning" />
                            )}
                            {tally.unlocked}/{tally.total}
                          </span>
                        </SidebarMenuBadge>
                      )}
                    </SidebarMenuItem>
                  );
                })}
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
