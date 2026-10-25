import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";
import MainLayout from "@/layouts/main-layout";
import { PlainLayout } from "@/layouts/plain-layout";
import { TrendingUp, Coins, Wallet, Bot, Trophy, Settings, Grid3x3, Gauge, Flag, Medal, Banknote, Landmark, Gavel } from "lucide-react";
import type { NavItem } from "@/types";
import VariableIncomePage from "@/features/variable-income/pages/variable-income";
import VariableIncomeDetailPage from "@/features/variable-income/pages/variable-income-details";
import ElectionPage from "./features/government/pages/election";
import GovernmentPage from "./features/government/pages/government";
import PortfolioPage from "./features/portfolio/pages/portfolio";
import SettingsPage from "./features/settings/pages/settings";
import FixedIncomePage from "./features/fixed-income/pages/fixed-income";
import FixedIncomeDetailPage from "./features/fixed-income/pages/fixed-income-details";
import StrategiesPage from "./features/strategies/pages/strategies";
import PerformancePage from "./features/performance/pages/performance";
import { JoinMatchPage } from "./features/join/pages/join-match";
import { LobbyPage } from "./features/lobby/pages/lobby";
import BacktestNewPage from "./features/backtest/pages/backtest-new";
import BacktestRunningPage from "./features/backtest/pages/backtest-running";
import ImportAssetsPage from "./features/import-assets/pages/import-assets";
import { RealtimeProvider } from "@/shared/context/realtime";
import { Toaster } from "@/shared/components/ui/sonner";
import { PageLabelProvider } from "@/shared/context/page-label";
import GoalPage from "./features/goal/pages/goal";
import CreditPage from "./features/credit/pages/credit";
import StatisticsPage from "./features/statistics/pages/statistics";
import CompareSimulationsPage from "./features/statistics/pages/compare-simulations";
import MatchResultPage from "./features/statistics/pages/match-result";
import AchievementsPage from "./features/achievements/pages/achievements";
import CorrelationPage from "./features/correlation/pages/correlation";
import { LoginPage } from "./features/auth/pages/login";
import { AuthProvider } from "./shared/context/auth";
import { ErrorPage } from "./pages/error";
import { NotificationSettingsProvider } from "@/shared/context/notifications-settings";
import { GlobalNotifications } from "./shared/notifications";
import { GovernmentNotifications } from "./features/government/components/government-notifications";
import { SimulationProvider } from "./shared/context/simulation";
import { GuardLayout } from "./layouts/guard-layout";
import { SimulationModeLayout } from "./layouts/simulation-mode-layout";
import { queryClient } from "@/shared/lib/queryClient";
import { DebugTools } from "@/shared/components/debug-tools";

const navItems: NavItem[] = [
  { key: "variable-income", label: "Renda variável", endpoint: "/variable-income", icon: TrendingUp, group: "Mercado" },
  { key: "fixed-income", label: "Renda fixa", endpoint: "/fixed-income", icon: Coins, group: "Mercado" },
  { key: "portfolio", label: "Carteira", endpoint: "/portfolio", icon: Wallet, group: "Você" },
  { key: "goal", label: "Meta", endpoint: "/goal", icon: Flag, group: "Você", goalOnly: true },
  { key: "credit", label: "Crédito", endpoint: "/credit", icon: Banknote, group: "Você", creditAlert: true },
  { key: "statistics", label: "Estatísticas", endpoint: "/statistics", icon: Trophy, group: "Você" },
  { key: "achievements", label: "Conquistas", endpoint: "/achievements", icon: Medal, group: "Você", achievementTally: true },
  { key: "election", label: "Eleição", endpoint: "/election", icon: Landmark, group: "Expansões", expansion: "government" },
  { key: "government", label: "Governo", endpoint: "/government", icon: Gavel, group: "Expansões", expansion: "government" },
  { key: "correlation", label: "Correlação", endpoint: "/correlation", icon: Grid3x3, group: "Ferramentas" },
  { key: "strategies", label: "Estratégias", endpoint: "/strategies", icon: Bot, group: "Ferramentas", strategyStatus: true },
  { key: "performance", label: "Desempenho", endpoint: "/performance", icon: Gauge, group: "Ferramentas", badge: "Debug", badgeTone: "warning", debugOnly: true },
  { key: "settings", label: "Configurações", endpoint: "/settings", icon: Settings, group: "Ferramentas" },
];

const routeLabels = navItems.reduce<Record<string, string>>((acc, item) => {
  acc[item.endpoint] = item.label;
  return acc;
}, {});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      {/* A troca de rota é urgente: o fim da partida leva ao resultado antes do status inativo chegar ao guard */}
      <BrowserRouter useTransitions={false}>
        <AuthProvider>
          <RealtimeProvider>
            <NotificationSettingsProvider>
              {/* Listeners globais de notificações */}
              <GlobalNotifications />
              <GovernmentNotifications />
              <DebugTools />
              <PageLabelProvider routeLabels={routeLabels}>
                <SimulationProvider>
                  <Routes>
                    <Route element={<GuardLayout />}>
                      <Route path="/login" element={<LoginPage />} />
                      <Route path="/lobby" element={<LobbyPage />} />
                      <Route path="/join" element={<JoinMatchPage />} />
                      <Route element={<PlainLayout />}>
                        <Route path="/backtest/new" element={<BacktestNewPage />} />
                        <Route path="/backtest/running" element={<BacktestRunningPage />} />
                        <Route path="/import-assets" element={<ImportAssetsPage />} />
                        <Route path="/compare-simulations" element={<CompareSimulationsPage />} />
                        <Route path="/match-result/:simulationId" element={<MatchResultPage />} />
                      </Route>
                      <Route element={<MainLayout navItems={navItems} />}>
                        <Route path="/" element={<PortfolioPage />} />
                        <Route path="/variable-income" element={<VariableIncomePage />} />
                        <Route path="/variable-income/:ticker" element={<VariableIncomeDetailPage />} />
                        <Route path="/fixed-income" element={<FixedIncomePage />} />
                        <Route path="/fixed-income/:id" element={<FixedIncomeDetailPage />} />
                        <Route path="/portfolio" element={<PortfolioPage />} />
                        <Route path="/strategies" element={<StrategiesPage />} />
                        <Route path="/performance" element={<PerformancePage />} />
                        <Route path="/settings" element={<SettingsPage />} />
                        <Route path="/goal" element={<GoalPage />} />
                        <Route path="/credit" element={<CreditPage />} />
                        <Route path="/statistics" element={<StatisticsPage />} />
                        <Route path="/election" element={<ElectionPage />} />
                        <Route path="/government" element={<GovernmentPage />} />
                      </Route>
                      <Route element={<SimulationModeLayout navItems={navItems} />}>
                        <Route path="/correlation" element={<CorrelationPage />} />
                        <Route path="/achievements" element={<AchievementsPage />} />
                      </Route>
                    </Route>
                    {/* 404 */}
                    <Route path="*" element={<ErrorPage />} />
                  </Routes>
                  <Toaster position="bottom-right" />
                </SimulationProvider>
              </PageLabelProvider>
            </NotificationSettingsProvider>
          </RealtimeProvider>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
