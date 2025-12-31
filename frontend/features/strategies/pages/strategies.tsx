import { useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSyncAlt, faRobot, faHandPaper, faTrashAlt } from "@fortawesome/free-solid-svg-icons";

interface Strategy {
  value: string;
  title: string;
  description: string;
}

const strategies: Strategy[] = [
  {
    value: "moving-average",
    title: "Média Móvel 50/200",
    description: "Compra quando média de 50 dias cruza acima de 200 dias",
  },
  {
    value: "rsi",
    title: "RSI Oversold/Overbought",
    description: "Compra quando RSI < 30, vende quando RSI> 70",
  },
  {
    value: "breakout",
    title: "Breakout Trading",
    description: "Compra quando preço rompe resistência com volume",
  },
];

const initialLog = [
  { text: "[10:30:05] PETR4: Compra realizada - 100 ações @ R$32.45", type: "green" },
  { text: "[11:15:22] VALE3: Venda realizada - 50 ações @ R$67.89", type: "red" },
  { text: "[11:45:18] Nenhum sinal identificado nas últimas 30 velas", type: "default" },
  { text: "[12:00:00] Analisando 5 ativos no momento...", type: "gray" },
  { text: "[12:30:15] ITUB4: Compra realizada - 200 ações @ R$28.12", type: "green" },
];

export default function StrategiesPage() {
  const [mode, setMode] = useState<"auto" | "manual">("auto");
  const [selectedStrategy, setSelectedStrategy] = useState<string>("moving-average");
  const [log, setLog] = useState(initialLog);

  const handleModeChange = (newMode: "auto" | "manual") => setMode(newMode);

  const handleStrategyChange = (value: string) => setSelectedStrategy(value);

  const handleRefresh = () => {
    // placeholder de refresh
    console.log("Refresh strategies...");
  };

  const handleClearLog = () => setLog([]);

  return (
    <section id="strategies" className="section-content p-4">
      <div className="bg-white rounded-lg shadow p-6 space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold">Estratégias Automatizadas</h2>
          <button
            className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md flex items-center gap-2"
            onClick={handleRefresh}
          >
            <FontAwesomeIcon icon={faSyncAlt} /> Refresh
          </button>
        </div>

        {/* Strategy Selection Panel */}
        <div className="border rounded-lg p-4 space-y-4">
          {/* Mode Selection */}
          <div className="mb-6">
            <h3 className="font-medium mb-2">Modo de Execução</h3>
            <div className="flex space-x-4">
              <button
                className={`flex-1 py-3 px-4 rounded-lg shadow transition flex items-center justify-center gap-2 ${
                  mode === "auto" ? "bg-blue-600 text-white hover:bg-blue-700" : "bg-gray-100 hover:bg-gray-200"
                }`}
                onClick={() => handleModeChange("auto")}
              >
                <FontAwesomeIcon icon={faRobot} /> Automático
              </button>
              <button
                className={`flex-1 py-3 px-4 rounded-lg shadow transition flex items-center justify-center gap-2 ${
                  mode === "manual" ? "bg-blue-600 text-white hover:bg-blue-700" : "bg-gray-100 hover:bg-gray-200"
                }`}
                onClick={() => handleModeChange("manual")}
              >
                <FontAwesomeIcon icon={faHandPaper} /> Manual
              </button>
            </div>
          </div>

          {/* Strategy Options */}
          <h3 className="font-medium mb-4">Estratégias Disponíveis</h3>
          <div className="space-y-2">
            {strategies.map((s) => (
              <label
                key={s.value}
                className="flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100 rounded-lg cursor-pointer transition"
              >
                <div>
                  <h4 className="font-medium">{s.title}</h4>
                  <p className="text-sm text-gray-500">{s.description}</p>
                </div>
                <div className="relative">
                  <input
                    type="radio"
                    name="strategy"
                    value={s.value}
                    className="sr-only peer"
                    checked={selectedStrategy === s.value}
                    onChange={() => handleStrategyChange(s.value)}
                  />
                  <div className="w-6 h-6 border-2 border-gray-300 rounded-full peer-checked:border-blue-600 flex items-center justify-center transition">
                    <div className="w-3 h-3 rounded-full bg-blue-600 opacity-0 peer-checked:opacity-100 transition"></div>
                  </div>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Log Output */}
        <div className="border rounded-lg p-4">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-medium">Log de Execução</h3>
            <button className="text-gray-500 hover:text-gray-700" onClick={handleClearLog}>
              <FontAwesomeIcon icon={faTrashAlt} />
            </button>
          </div>
          <div className="h-48 overflow-y-auto bg-gray-100 rounded p-3 font-mono text-sm space-y-1">
            {log.map((entry, idx) => {
              let colorClass = "text-gray-800";
              if (entry.type === "green") colorClass = "text-green-600";
              if (entry.type === "red") colorClass = "text-red-600";
              if (entry.type === "gray") colorClass = "text-gray-400";

              return (
                <div key={idx} className={colorClass}>
                  {entry.text}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
