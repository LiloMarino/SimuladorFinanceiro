import { BrowserRouter, Routes, Route } from "react-router-dom";
import MainLayout from "@/layouts/main-layout";
import {
  faChartLine,
  faCoins,
  faWallet,
  faFileImport,
  faRobot,
  faTrophy,
  faDoorOpen,
  faCog,
} from "@fortawesome/free-solid-svg-icons";
import type { NavItem } from "@/types";
import VariableIncomePage from "@/features/variable-income/pages/variable-income";
import VariableIncomeDetailPage from "@/features/variable-income/pages/variable-income-details";
import PortfolioPage from "./features/portfolio/pages/portfolio";
import SettingsPage from "./pages/settings";
import FixedIncomePage from "./features/fixed-income/pages/fixed-income";
import FixedIncomeDetailPage from "./features/fixed-income/pages/fixed-income-details";
import StrategiesPage from "./pages/strategies";
import { LobbyHostPage } from "./pages/lobby";
import ImportAssetsPage from "./features/import-assets/pages/import-assets";
import { RealtimeProvider } from "@/shared/context/realtime";
import { Toaster } from "@/shared/components/ui/sonner";
import { PageLabelProvider } from "@/shared/context/page-label";
import StatisticsPage from "./pages/statistics";
import { LoginPage } from "./features/auth/pages/login";

const navItems: NavItem[] = [
  { key: "variable-income", label: "Renda Variável", endpoint: "/variable-income", icon: faChartLine },
  { key: "fixed-income", label: "Renda Fixa", endpoint: "/fixed-income", icon: faCoins },
  { key: "portfolio", label: "Carteira", endpoint: "/portfolio", icon: faWallet },
  { key: "import-assets", label: "Importar Ativos", endpoint: "/import-assets", icon: faFileImport },
  { key: "strategies", label: "Estratégias", endpoint: "/strategies", icon: faRobot },
  { key: "statistics", label: "Estatísticas", endpoint: "/statistics", icon: faTrophy },
  { key: "lobby", label: "Sala Multiplayer", endpoint: "/lobby", icon: faDoorOpen },
  { key: "settings", label: "Configurações", endpoint: "/settings", icon: faCog },
];

const routeLabels = navItems.reduce<Record<string, string>>((acc, item) => {
  acc[item.endpoint] = item.label;
  return acc;
}, {});

export default function App() {
  return (
    <RealtimeProvider mode="ws">
      <PageLabelProvider routeLabels={routeLabels}>
        <BrowserRouter>
          <MainLayout navItems={navItems}>
            <Routes>
              <Route path="/" element={<PortfolioPage />} />
              <Route path="/variable-income" element={<VariableIncomePage />} />
              <Route path="/variable-income/:ticker" element={<VariableIncomeDetailPage />} />
              <Route path="/fixed-income" element={<FixedIncomePage />} />
              <Route path="/fixed-income/:id" element={<FixedIncomeDetailPage />} />
              <Route path="/portfolio" element={<PortfolioPage />} />
              <Route path="/strategies" element={<StrategiesPage />} />
              <Route path="/settings" element={<SettingsPage />} />
              <Route path="/statistics" element={<StatisticsPage />} />
              <Route path="/lobby/host" element={<LobbyHostPage />} />
              <Route path="/lobby/client" element={<LoginPage />} />
              <Route path="/import-assets" element={<ImportAssetsPage />} />
            </Routes>
            <Toaster position="bottom-right" richColors />
          </MainLayout>
        </BrowserRouter>
      </PageLabelProvider>
    </RealtimeProvider>
  );
}
