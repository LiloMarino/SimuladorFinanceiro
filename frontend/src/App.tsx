import { BrowserRouter, Routes, Route } from "react-router-dom";
import Example from "@/pages/example";
import MainLayout from "@/layouts/main-layout";
import { 
  faChartLine, 
  faCoins, 
  faWallet, 
  faFileImport, 
  faRobot, 
  faTrophy, 
  faDoorOpen, 
  faCog 
} from "@fortawesome/free-solid-svg-icons";
import type { NavItem } from "@/types";
import VariableIncomePage from "@/pages/variable-income";
import StockDetailPage from "@/pages/stock-details";
import PortfolioPage from "./pages/portfolio";
import SettingsPage from "./pages/settings";
import FixedIncomePage from "./pages/fixed-income";
import FixedIncomeDetailPage from "./pages/fixed-income-details";
import StrategiesPage from "./pages/strategies";
import StatisticsPage from "./pages/statistics";

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

export default function App() {
  return (
    <BrowserRouter>
      <MainLayout navItems={navItems} simulationTime="00/00/0000">
        <Routes>
          <Route path="/" element={<Example />} />
          <Route path="/variable-income" element={<VariableIncomePage />} />
          <Route path="/variable-income/:ticker" element={<StockDetailPage />} />
          <Route path="/fixed-income" element={<FixedIncomePage />} />
          <Route path="/fixed-income/:product" element={<FixedIncomeDetailPage />} />
          <Route path="/portfolio" element={<PortfolioPage />} />
          <Route path="/strategies" element={<StrategiesPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/statistics" element={<StatisticsPage />} />
        </Routes>
      </MainLayout>
    </BrowserRouter>
  );
}
