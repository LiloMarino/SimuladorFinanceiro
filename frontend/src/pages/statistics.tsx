import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faMedal, faTrophy, faBolt } from "@fortawesome/free-solid-svg-icons";

interface PlayerStat {
  position: number;
  name: string;
  equity: number;
  returnPct: string;
}

interface Achievement {
  icon: any;
  color: string;
  text: string;
}

interface StatsPageProps {
  players: PlayerStat[];
  achievements?: Achievement[];
}

export default function StatisticsPage({
  players = [
    { position: 1, name: "Você", equity: 125430.65, returnPct: "+12.3%" },
    { position: 2, name: "Ana_Silva", equity: 118540.2, returnPct: "+9.8%" },
    { position: 3, name: "Carlos_Invest", equity: 107890.75, returnPct: "+7.2%" },
    { position: 4, name: "Bia_Trader", equity: 98450.3, returnPct: "+5.5%" },
    { position: 5, name: "Pedro_Bolsa", equity: 87670.15, returnPct: "-2.1%" },
  ],
  achievements = [
    { icon: faMedal, color: "text-yellow-500", text: "Melhor Retorno do Dia (+2.4%)" },
    { icon: faTrophy, color: "text-blue-500", text: "Líder do Ranking (3 dias)" },
    { icon: faBolt, color: "text-purple-500", text: "Estratégia Mais Rentável" },
  ],
}: StatsPageProps) {
  return (
    <section id="stats" className="section-content p-4">
      <div className="bg-white rounded-lg shadow p-6 space-y-6">
        <h2 className="text-xl font-semibold mb-6">Estatísticas Multiplayer</h2>

        {/* Ranking de Jogadores */}
        <div>
          <h3 className="font-medium mb-2">Ranking de Jogadores</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  {["Posição", "Jogador", "Patrimônio", "Retorno %"].map((h) => (
                    <th
                      key={h}
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {players.map((player) => (
                  <tr key={player.position}>
                    <td className="px-6 py-4 whitespace-nowrap font-medium">{player.position}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{player.name}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      R$ {player.equity.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </td>
                    <td
                      className={`px-6 py-4 whitespace-nowrap ${
                        player.returnPct.startsWith("-") ? "text-red-600" : "text-green-600"
                      }`}
                    >
                      {player.returnPct}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Charts & Achievements */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Performance Chart */}
          <div className="border rounded-lg p-4">
            <h3 className="font-medium mb-4">Desempenho da Partida</h3>
            <div className="h-48 bg-gray-100 rounded flex items-center justify-center">
              <p className="text-gray-500">Gráfico comparativo de performance</p>
            </div>
          </div>

          {/* Achievements */}
          <div className="border rounded-lg p-4">
            <h3 className="font-medium mb-4">Conquistas</h3>
            <div className="space-y-3">
              {achievements.map((ach, idx) => (
                <div key={idx} className="flex items-center">
                  <FontAwesomeIcon icon={ach.icon} className={`${ach.color} mr-2`} />
                  <span className="text-sm">{ach.text}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
