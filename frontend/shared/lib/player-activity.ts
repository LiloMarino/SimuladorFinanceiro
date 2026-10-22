import { matchPath } from "react-router-dom";
import type { PlayerActivity } from "@/types";

/** Texto curto do selo (cabe nos ~86 px do cartão do lobby) e a frase inteira da dica. */
export const PLAYER_ACTIVITIES: Record<PlayerActivity, { label: string; hint: string }> = {
  lobby: { label: "No lobby", hint: "No lobby" },
  import_assets: { label: "Na Central", hint: "Na Central de dados" },
  compare_simulations: { label: "Comparando", hint: "Comparando simulações" },
  match_result: { label: "No resultado", hint: "Vendo o resultado de uma partida" },
  settings: { label: "Configurando", hint: "Nas configurações" },
  menus: { label: "Nos menus", hint: "Navegando nos menus" },
  away: { label: "Ausente", hint: "Saiu da aba do jogo" },
};

/** Telas com atividade própria; tela nova ganha a dela acrescentando uma linha aqui e no mapa acima. */
const ROUTE_ACTIVITIES: { path: string; activity: PlayerActivity }[] = [
  { path: "/lobby", activity: "lobby" },
  { path: "/import-assets", activity: "import_assets" },
  { path: "/compare-simulations", activity: "compare_simulations" },
  { path: "/match-result/:simulationId", activity: "match_result" },
  { path: "/settings", activity: "settings" },
];

/** A atividade de quem está em `pathname`; rota fora do mapa é "menus". */
export function activityForPath(pathname: string): PlayerActivity {
  return ROUTE_ACTIVITIES.find(({ path }) => matchPath(path, pathname))?.activity ?? "menus";
}
