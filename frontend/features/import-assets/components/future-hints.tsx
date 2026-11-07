import type { ReactNode } from "react";
import { InfoHint } from "@/shared/components/info-hint";
import { SortableTableHead } from "@/shared/components/sortable-table-head";
import { useTableSort } from "@/shared/hooks/useTableSort";
import { displayNumber } from "@/shared/lib/utils/display";
import {
  INFLATION_LEVEL_TABLE,
  signedLevel,
  SURGE_FREQUENCY_TABLE,
  TEMPERATURE_TABLE,
  withMinus,
} from "../lib/future-readings";

type HintRow = { values: number[]; cells: ReactNode[] };

function HintTable({ head, rows }: { head: string[]; rows: HintRow[] }) {
  const sorting = useTableSort(
    rows,
    Object.fromEntries(head.map((_, index) => [String(index), (row: HintRow) => row.values[index]])),
  );
  return (
    <table className="mt-1 w-full border-collapse text-xs tabular-nums">
      <thead>
        <tr className="opacity-70">
          {head.map((cell, index) => (
            <SortableTableHead
              key={cell}
              label={cell}
              {...sorting.header(String(index))}
              numeric={index > 0}
              variant="hint"
            />
          ))}
        </tr>
      </thead>
      <tbody>
        {sorting.rows.map((row) => (
          <tr key={row.values[0]}>
            {row.cells.map((cell, index) => (
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
    <InfoHint label="O que é temperatura" interactive>
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
          rows={TEMPERATURE_TABLE.map((row) => ({
            values: [row.level, row.volatility, row.crashYears],
            cells: [row.level, `${row.volatility}%`, `${row.crashYears} de 100`],
          }))}
        />
        <p className="opacity-70">100 futuros de 5 anos. O pior ano real desde 2000 foi 2008, com 52%.</p>
      </div>
    </InfoHint>
  );
}

export function InflationLevelHint() {
  return (
    <InfoHint label="O que é o nível da inflação" interactive>
      <div className="space-y-1.5 text-left">
        <p className="font-semibold">Nível da inflação</p>
        <p>
          Soma pontos à inflação anual do futuro inteiro: a alta leva seis meses e fica. A SELIC sobe 1,5 vez o que a
          inflação subiu, como o Banco Central faz para conter a alta, e depois assenta em 1 vez, de modo que o juro
          real volta ao de antes. A bolsa cai enquanto o juro real está alto e recupera quando a SELIC assenta: no longo
          prazo a inflação só infla os preços, e a bolsa acompanha.
        </p>
        <p>
          <b>Juro real</b> é a SELIC descontada a inflação: SELIC de 14% com inflação de 6% rende uns 8% acima dos
          preços. <b>Tombo da bolsa</b> é o quanto o Ibovespa, descontada a inflação, chega a ficar abaixo do mesmo
          futuro sem nível: −13% quer dizer que, no pior momento, o dinheiro na bolsa compra 13% a menos do que
          compraria sem a inflação extra.
        </p>
        <HintTable
          head={["Nível", "Inflação média", "SELIC média", "Tombo da bolsa", "Volta em"]}
          rows={INFLATION_LEVEL_TABLE.map((row) => ({
            values: [row.level, row.inflation, row.selic, row.stocksSwing, row.recoveryYears],
            cells: [
              signedLevel(row.level),
              `${row.inflation}% ao ano`,
              `${row.selic}% ao ano`,
              row.stocksSwing === 0 ? "—" : withMinus(`${row.stocksSwing > 0 ? "+" : ""}${row.stocksSwing}%`),
              row.recoveryYears === 0 ? "—" : `${row.recoveryYears} anos`,
            ],
          }))}
        />
        <p className="opacity-70">
          Medianas de 50 futuros de 10 anos partindo de hoje; o tombo chega no sexto mês. Com o nível negativo é o
          inverso: o juro cai e a bolsa sobe na transição. Em 10 anos a bolsa real fica parecida em qualquer nível, uns
          +19% no futuro do meio, com extremos de −67% a +337%.
        </p>
      </div>
    </InfoHint>
  );
}

export function SurgeFrequencyHint() {
  return (
    <InfoHint label="O que são os surtos de inflação" interactive>
      <div className="space-y-1.5 text-left">
        <p className="font-semibold">Frequência dos surtos</p>
        <p>
          Surto é uma alta de inflação que sobe em seis meses e perde metade da força a cada ano, com a SELIC subindo
          1,5 vez o que a inflação subiu. Cada ano da série tem a própria chance de começar um: 3 surtos por década são
          3 chances em 10.
        </p>
        <p>
          Com a mesma semente, aumentar a frequência só acrescenta surtos, sem mexer nos que já estavam. Surtos próximos
          se somam.
        </p>
        <HintTable
          head={["Surtos por década", "Anos com inflação acima de 10%"]}
          rows={SURGE_FREQUENCY_TABLE.map((row) => ({
            values: [row.frequency, row.hotYears],
            cells: [row.frequency, `${displayNumber(row.hotYears, 1)} de 10`],
          }))}
        />
        <p className="opacity-70">Médias de 50 futuros de 10 anos, com surtos de 6 pontos e sem nível extra.</p>
      </div>
    </InfoHint>
  );
}

export function SurgeIntensityHint() {
  return (
    <InfoHint label="O que é a intensidade dos surtos">
      <div className="space-y-1.5 text-left">
        <p className="font-semibold">Intensidade dos surtos</p>
        <p>
          Quantos pontos um surto soma à inflação anual no pico, seis meses depois de começar. É a média: cada surto
          sorteia entre metade e uma vez e meia esse valor. Sem surtos, a intensidade não faz nada.
        </p>
      </div>
    </InfoHint>
  );
}
