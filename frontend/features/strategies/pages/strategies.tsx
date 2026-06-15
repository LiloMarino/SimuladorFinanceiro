import { useState } from "react";
import { RefreshCw, Bot, Hand, Trash2 } from "lucide-react";
import { ErrorPage } from "@/pages/error";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";

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

  const handleStrategyChange = (value: string) => setSelectedStrategy(value);
  const handleClearLog = () => setLog([]);

  return <ErrorPage code="501" title="Página em desenvolvimento" message="Em breve..." />;
  return (
    <section id="strategies" className="section-content p-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Estratégias Automatizadas</CardTitle>
          <Button>
            <RefreshCw /> Refresh
          </Button>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Strategy Selection Panel */}
          <Card>
            <CardContent className="pt-6 space-y-4">
              {/* Mode Selection */}
              <div>
                <h3 className="font-medium mb-2">Modo de Execução</h3>
                <div className="flex gap-4">
                  <Button
                    className="flex-1"
                    variant={mode === "auto" ? "default" : "outline"}
                    onClick={() => setMode("auto")}
                  >
                    <Bot /> Automático
                  </Button>
                  <Button
                    className="flex-1"
                    variant={mode === "manual" ? "default" : "outline"}
                    onClick={() => setMode("manual")}
                  >
                    <Hand /> Manual
                  </Button>
                </div>
              </div>

              {/* Strategy Options */}
              <div>
                <h3 className="font-medium mb-3">Estratégias Disponíveis</h3>
                <div className="space-y-2">
                  {strategies.map((s) => (
                    <label
                      key={s.value}
                      className="flex items-center justify-between p-4 rounded-lg border cursor-pointer transition hover:bg-accent"
                    >
                      <div>
                        <h4 className="font-medium">{s.title}</h4>
                        <p className="text-sm text-muted-foreground">{s.description}</p>
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
                        <div className="w-6 h-6 border-2 border-muted-foreground rounded-full peer-checked:border-primary flex items-center justify-center transition">
                          <div className="w-3 h-3 rounded-full bg-primary opacity-0 peer-checked:opacity-100 transition" />
                        </div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Log Output */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <h3 className="font-medium">Log de Execução</h3>
              <Button variant="ghost" size="icon" aria-label="Limpar log" onClick={handleClearLog}>
                <Trash2 />
              </Button>
            </CardHeader>
            <CardContent>
              <div className="h-48 overflow-y-auto bg-muted rounded p-3 font-mono text-sm space-y-1">
                {log.map((entry, idx) => {
                  let colorClass = "text-foreground";
                  if (entry.type === "green") colorClass = "text-success";
                  if (entry.type === "red") colorClass = "text-destructive";
                  if (entry.type === "gray") colorClass = "text-muted-foreground";

                  return (
                    <div key={idx} className={colorClass}>
                      {entry.text}
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </CardContent>
      </Card>
    </section>
  );
}
