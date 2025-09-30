interface TopbarProps {
  pageLabel: string;
  simulationTime: string;
}

export default function Topbar({ pageLabel, simulationTime }: TopbarProps) {
  return (
    <header className="bg-white shadow-sm">
      <div className="flex items-center justify-between p-4">
        <h1 className="text-xl font-semibold text-gray-800">{pageLabel}</h1>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600 hidden md:block">Velocidade:</span>
          <div className="flex bg-gray-200 rounded-md divide-x divide-gray-300 overflow-hidden">
            {[0, 1, 2, 4, 10].map((speed) => (
              <button
                key={speed}
                className={`speed-btn px-3 py-1 text-sm ${speed === 0 ? "active-speed" : ""}`}
                data-speed={speed}
              >
                {speed === 0 ? "Pausar" : `${speed}x`}
              </button>
            ))}
          </div>
          <div className="ml-4 flex items-center">
            <span className="text-sm text-gray-600 mr-2">Simulação:</span>
            <span id="simulation-time" className="font-medium">{simulationTime}</span>
          </div>
        </div>
      </div>
    </header>
  );
}
