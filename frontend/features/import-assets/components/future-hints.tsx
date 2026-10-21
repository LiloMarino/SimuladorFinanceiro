import type { ReactNode } from "react";
import { InfoHint } from "@/shared/components/info-hint";
import { withMinus, INFLATION_SHOCK_TABLE, signedShock, TEMPERATURE_TABLE } from "../lib/future-readings";

function HintTable({ head, rows }: { head: string[]; rows: ReactNode[][] }) {
  return (
    <table className="mt-1 w-full border-collapse text-xs tabular-nums">
      <thead>
        <tr className="opacity-70">
          {head.map((cell, index) => (
            <th key={cell} className={index === 0 ? "py-0.5 pr-2 text-left font-medium" : "px-1.5 py-0.5 text-right font-medium"}>
              {cell}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.map((row, rowIndex) => (
          <tr key={rowIndex}>
            {row.map((cell, index) => (
              <td key={index} className={index === 0 ? "py-0.5 pr-2 text-left" : "px-1.5 py-0.5 text-right"}>
                {cell}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export function TemperatureHint() {
  return (
    <InfoHint label="O que é temperatura">
      <div className="space-y-1.5 text-left">
        <p className="font-semibold">Temperatura</p>
        <p>
          Como a de uma IA que escreve texto: em 1 o sorteio segue o histórico como foi; abaixo, prefere trechos calmos;
          acima, os agitados.
        </p>
        <p>
          <b>Volatilidade</b> é o quanto o Ibovespa costuma oscilar num ano: 24% quer dizer que um ano típico sobe ou
          cai uns 24% em torno da média.
        </p>
        <HintTable
          head={["Temp.", "Oscila no ano", "Anos com queda >30%"]}
          rows={TEMPERATURE_TABLE.map((row) => [row.level, `${row.volatility}%`, `${row.crashYears} de 100`])}
        />
        <p className="opacity-70">100 futuros de 5 anos. O pior ano real desde 2000 foi 2008, com 52%.</p>
      </div>
    </InfoHint>
  );
}

export function StartRegimeHint() {
  return (
    <InfoHint label="O que é o clima inicial">
      <div className="space-y-1.5 text-left">
        <p className="font-semibold">Começar em</p>
        <p>
          O mercado alterna entre três climas, pela agitação do Ibovespa: calmaria (o terço mais calmo do histórico),
          normal e crise (o terço mais agitado).
        </p>
        <p>
          A escolha vale só para o primeiro trimestre. Depois o clima muda sozinho, com as chances medidas no histórico:
          crise tende a ser seguida de crise.
        </p>
      </div>
    </InfoHint>
  );
}

export function InflationShockHint() {
  return (
    <InfoHint label="O que é o choque de inflação">
      <div className="space-y-1.5 text-left">
        <p className="font-semibold">Choque de inflação</p>
        <p>
          Soma pontos à inflação anual: cresce em seis meses e depois perde metade da força a cada ano. A SELIC sobe 1,5
          vez o que a inflação subiu, como o Banco Central faz para conter a alta.
        </p>
        <HintTable
          head={["Choque", "Inflação no pico", "SELIC no pico", "Queda em 2 anos"]}
          rows={INFLATION_SHOCK_TABLE.map((row) => [
            signedShock(row.shock),
            `${row.inflationPeak}%`,
            `${row.selicPeak}%`,
            withMinus(`${row.twoYearDrop}%`),
          ])}
        />
        <p className="opacity-70">Medianas de 50 futuros partindo de hoje, com a SELIC em 13,65%.</p>
      </div>
    </InfoHint>
  );
}
