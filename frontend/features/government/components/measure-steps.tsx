import { displayDayMonth, displayMonthShort } from "@/shared/lib/utils/display";
import type { GovernmentPanel } from "@/types";
import { effectiveDate } from "../lib/government";

type Step = { title: string; when: string; text: string };
type Steps = [Step, Step, Step, Step];
type StepsPanel = Pick<GovernmentPanel, "today" | "next_vote" | "vigence_days">;

function steps(panel: StepsPanel): Steps {
  const effective = effectiveDate(panel.next_vote, panel.vigence_days);
  return [
    {
      title: "Proposta",
      when: displayDayMonth(panel.today),
      text: "A medida entra na fila na hora, sem pausar a partida. A sala vê a fila e já pode se mexer.",
    },
    {
      title: "Votação no Congresso",
      when: displayDayMonth(panel.next_vote),
      text: "No fechamento do mês, o Congresso vota a fila inteira. Cada medida passa com chance igual à aprovação do governo naquele dia.",
    },
    {
      title: `Espera de ${panel.vigence_days} dias`,
      when: `${displayMonthShort(panel.next_vote)} → ${displayMonthShort(effective)}`,
      text: "Como a noventena, a regra que o Brasil usa para imposto novo, a medida aprovada só vale depois da espera, e a sala tem tempo de se ajustar.",
    },
    {
      title: "Passa a valer",
      when: displayDayMonth(effective),
      text: "O imposto muda para todos. Imposto vale em qualquer período da história, porque não mexe em preço.",
    },
  ];
}

/** Os quatro passos de uma medida, com as datas da próxima votação. */
export function MeasureSteps({ panel }: { panel: StepsPanel }) {
  const list = steps(panel);
  const effective = list[3].when;
  return (
    <div className="grid w-80 gap-2.5">
      <ol className="grid gap-0">
        {list.map((step, index) => (
          <li key={step.title} className="relative grid grid-cols-[28px_1fr] gap-3 pb-4 last:pb-0">
            {index < list.length - 1 && <span className="absolute top-7.5 -bottom-1.5 left-3.25 w-0.5 bg-border" />}
            <span className="relative inline-flex size-7 items-center justify-center rounded-full bg-info-soft font-mono text-xs font-semibold text-info">
              {index + 1}
            </span>
            <span className="grid gap-0.5">
              <span className="flex items-baseline gap-2">
                <b className="text-sm">{step.title}</b>
                <span className="font-mono text-xs text-muted-foreground">{step.when}</span>
              </span>
              <span className="text-[13px] leading-normal text-muted-foreground">{step.text}</span>
            </span>
          </li>
        ))}
      </ol>
      <p className="rounded-lg bg-subtle px-2.5 py-2 text-xs leading-normal text-muted-foreground">
        Exemplo: aprovada na votação de {list[1].when}, a medida vale em {effective}. A venda feita antes dessa data
        paga o imposto de antes.
      </p>
    </div>
  );
}
