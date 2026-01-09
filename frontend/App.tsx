import { BrowserRouter, Routes, Route } from "react-router-dom";
import MainLayout from "@/layouts/main-layout";
import {
  faChartLine,
  faCoins,
  faWallet,
  faFileImport,
  faRobot,
  faTrophy,
  faCog,
} from "@fortawesome/free-solid-svg-icons";
import type { NavItem } from "@/types";
import VariableIncomePage from "@/features/variable-income/pages/variable-income";
import VariableIncomeDetailPage from "@/features/variable-income/pages/variable-income-details";
import PortfolioPage from "./features/portfolio/pages/portfolio";
import SettingsPage from "./features/settings/pages/settings";
import FixedIncomePage from "./features/fixed-income/pages/fixed-income";
import FixedIncomeDetailPage from "./features/fixed-income/pages/fixed-income-details";
import StrategiesPage from "./features/strategies/pages/strategies";
import { LobbyPage } from "./features/lobby/pages/lobby";
import ImportAssetsPage from "./features/import-assets/pages/import-assets";
import { RealtimeProvider } from "@/shared/context/realtime";
import { Toaster } from "@/shared/components/ui/sonner";
import { PageLabelProvider } from "@/shared/context/page-label";
import StatisticsPage from "./features/statistics/pages/statistics";
import { LoginPage } from "./features/auth/pages/login";
import { AuthProvider } from "./shared/context/auth";
import { ErrorPage } from "./pages/error";
import { NotificationSettingsProvider } from "@/shared/context/notifications-settings";
import { GlobalNotifications } from "./shared/notifications";
import { SimulationProvider } from "./shared/context/simulation";
import { GuardLayout } from "./layouts/guard-layout";

const navItems: NavItem[] = [
  { key: "variable-income", label: "Renda Variável", endpoint: "/variable-income", icon: faChartLine },
  { key: "fixed-income", label: "Renda Fixa", endpoint: "/fixed-income", icon: faCoins },
  { key: "portfolio", label: "Carteira", endpoint: "/portfolio", icon: faWallet },
  { key: "statistics", label: "Estatísticas", endpoint: "/statistics", icon: faTrophy },
  { key: "strategies", label: "Estratégias", endpoint: "/strategies", icon: faRobot },
  { key: "import-assets", label: "Importar Ativos", endpoint: "/import-assets", icon: faFileImport },
  { key: "settings", label: "Configurações", endpoint: "/settings", icon: faCog },
];

const routeLabels = navItems.reduce<Record<string, string>>((acc, item) => {
  acc[item.endpoint] = item.label;
  return acc;
}, {});

export default function App() {
  return (
    <AuthProvider>
      <RealtimeProvider mode="ws">
        <NotificationSettingsProvider>
          {/* Listeners globais de notificações */}
          <GlobalNotifications />
          <PageLabelProvider routeLabels={routeLabels}>
            <SimulationProvider>
              <BrowserRouter>
                <Routes>
                  <Route element={<GuardLayout />}>
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/lobby" element={<LobbyPage />} />
                    <Route element={<MainLayout navItems={navItems} />}>
                      <Route path="/" element={<PortfolioPage />} />
                      <Route path="/variable-income" element={<VariableIncomePage />} />
                      <Route path="/variable-income/:ticker" element={<VariableIncomeDetailPage />} />
                      <Route path="/fixed-income" element={<FixedIncomePage />} />
                      <Route path="/fixed-income/:id" element={<FixedIncomeDetailPage />} />
                      <Route path="/portfolio" element={<PortfolioPage />} />
                      <Route path="/strategies" element={<StrategiesPage />} />
                      <Route path="/settings" element={<SettingsPage />} />
                      <Route path="/statistics" element={<StatisticsPage />} />
                      <Route path="/import-assets" element={<ImportAssetsPage />} />
                    </Route>
                  </Route>
                  {/* 404 */}
                  <Route path="*" element={<ErrorPage />} />
                </Routes>
                <Toaster position="bottom-right" richColors />
              </BrowserRouter>
            </SimulationProvider>
          </PageLabelProvider>
        </NotificationSettingsProvider>
      </RealtimeProvider>
    </AuthProvider>
  );
}
