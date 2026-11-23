import type { MetricInfo } from "@/shared/lib/metric-info";
import { displayPercent, displaySignedPercent } from "@/shared/lib/utils/display";
import type { IncomeSeries, LifeHistoryRow } from "@/types";
import {
  DOLLAR_CHANGE,
  GDP_12M,
  RETIREE_RAISE,
  SELIC_RATE,
  SERVANT_RAISE,
  STOCKS_RETURN,
  UNEMPLOYMENT,
  WELFARE_SPENDING,
} from "./profession-metrics";

type SeriesInfo = {
  title: string;
  /** O que o gráfico (ou a alavanca) mostra, em uma linha */
  subtitle: string;
  metric: MetricInfo;
  /** O valor de hoje do indicador */
  display: (value: string) => string;
};

/** Como cada indicador que mexe na renda se mostra na página. */
export const SERIES_INFO: Record<IncomeSeries["key"], SeriesInfo> = {
  GDP: {
    title: "PIB de 12 meses",
    subtitle: "Quanto a economia cresceu em um ano",
    metric: GDP_12M,
    display: (value) => displaySignedPercent(value, 1),
  },
  UNEMPLOYMENT: {
    title: "Desemprego",
    subtitle: "Move a chance de demissão",
    metric: UNEMPLOYMENT,
    display: (value) => displayPercent(value, 1),
  },
  DOLLAR: {
    title: "Variação do dólar",
    subtitle: "Em 12 meses",
    metric: DOLLAR_CHANGE,
    display: (value) => displaySignedPercent(value, 1),
  },
  SELIC: {
    title: "SELIC",
    subtitle: "Taxa ao ano",
    metric: SELIC_RATE,
    display: (value) => displayPercent(value, 2),
  },
  STOCKS: {
    title: "Retorno do Ibovespa",
    subtitle: "Em 12 meses",
    metric: STOCKS_RETURN,
    display: (value) => displaySignedPercent(value, 1),
  },
  SERVANT_RAISE: {
    title: "Aumento dos servidores",
    subtitle: "Acima do IPCA, decidido pelo governo da sala",
    metric: SERVANT_RAISE,
    display: (value) => `${displaySignedPercent(value, 1)} ao ano`,
  },
  RETIREE_RAISE: {
    title: "Reajuste dos aposentados",
    subtitle: "Acima do IPCA, decidido pelo governo da sala",
    metric: RETIREE_RAISE,
    display: (value) => `${displaySignedPercent(value, 1)} ao ano`,
  },
  WELFARE_SPENDING: {
    title: "Gasto com auxílio",
    subtitle: "Parte do PIB, decidida pelo governo da sala",
    metric: WELFARE_SPENDING,
    display: (value) => `${displayPercent(value, 1)} do PIB`,
  },
};

const multiple = (value: string) =>
  `${new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 2 }).format(Number(value))}×`;

/** A frase sob o gráfico: o lado do ponto neutro em que o indicador está e o que isso faz com a renda. */
export function todaySentence(series: IncomeSeries) {
  const effect = series.effect;
  if (effect === null) return null;
  const lead = leadOf(series);
  switch (series.effect_kind) {
    case "REAL_RAISE": {
      if (series.key === "GDP") {
        const unlocksOvertime = series.guides.some((guide) => guide.overtime);
        return {
          lead,
          text: `${
            Number(effect) > 0
              ? `reajuste de ${displaySignedPercent(effect, 1)} acima do IPCA.`
              : "reajuste só com o IPCA."
          }${unlocksOvertime ? " Acima de 0, hora extra liberada." : ""}`,
        };
      }
      const subject = series.key === "RETIREE_RAISE" ? "seu benefício" : "seu salário";
      return {
        lead,
        text:
          Number(effect) > 0
            ? `${subject} sobe ${displayPercent(effect, 1)} acima da inflação na virada do ano.`
            : `${subject} só acompanha a inflação na virada do ano.`,
      };
    }
    case "INCOME_FACTOR":
      return { lead, text: `sua renda fica em ${multiple(effect)} o valor normal.` };
    case "LAYOFF_FACTOR": {
      const times = Number(effect);
      return {
        lead,
        text: `chance de demissão em ${new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 2 }).format(times)} ${times <= 1 ? "vez" : "vezes"} a normal.`,
      };
    }
    case "BENEFIT":
      return { lead, text: `o auxílio paga ${multiple(effect)} o de referência.` };
  }
}

/** "Abaixo do neutro de 2%:" no indicador com ponto neutro; "Hoje:" na alavanca do governo. */
function leadOf(series: IncomeSeries) {
  if (series.neutral === null) return "Hoje:";
  const side = Number(series.current) - Number(series.neutral);
  const neutral = displayPercent(series.neutral, 1, { trim: true });
  if (side === 0) return `No neutro de ${neutral}:`;
  return `${side > 0 ? "Acima" : "Abaixo"} do neutro de ${neutral}:`;
}

/** O que o jogador fez na hora extra, diferente do que o jogo mudou sozinho. */
const PLAYER_ACTIONS = new Set(["overtime_on", "overtime_off"]);

export function isPlayerAction(row: LifeHistoryRow) {
  return row.kind === "PROFESSION_ACTION" && row.life_event_key !== null && PLAYER_ACTIONS.has(row.life_event_key);
}
