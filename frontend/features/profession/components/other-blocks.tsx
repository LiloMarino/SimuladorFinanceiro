import { KeyValueRow } from "@/shared/components/key-value-row";
import { MetricHint } from "@/shared/components/metric-hint";
import { displayDate, displayMoney, parseLocalDate } from "@/shared/lib/utils/display";
import type { ProfessionMechanic } from "@/types";
import { PARTY_MULTIPLE } from "../lib/profession-metrics";
import { BlockPanel, MechanicBlock } from "./mechanic-block";

const multiple = (value: string) =>
  `${new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 2 }).format(Number(value))}×`;

const electionIn = (months: number) => (months === 0 ? "neste mês" : `em ${months} ${months === 1 ? "mês" : "meses"}`);

type BlockOf<K extends ProfessionMechanic["kind"]> = { mechanic: Extract<ProfessionMechanic, { kind: K }> };

/** O que o Herdeiro tem no lugar de uma mecânica: a herança e quanto da despesa ela cobre. */
export function HeirBlock({ mechanic }: BlockOf<"heir">) {
  return (
    <MechanicBlock
      title="Sua herança"
      description="O patrimônio com que você começou a partida"
      links={[{ label: "Meta, quanto falta", to: "/goal" }]}
    >
      <BlockPanel title="Herança recebida">
        <KeyValueRow label="Valor" value={displayMoney(mechanic.inheritance)} />
        <KeyValueRow label="Recebida em" value={displayDate(parseLocalDate(mechanic.received_on))} />
        <KeyValueRow
          label="Cobre a despesa de"
          note={`com a despesa de ${displayMoney(mechanic.annual_expense)} por ano`}
          value={`${new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 1 }).format(Number(mechanic.covered_years))} anos`}
        />
      </BlockPanel>
    </MechanicBlock>
  );
}

/** O que o Comissionado tem no lugar de uma mecânica: o partido e a renda que ele dá. */
export function AppointeeBlock({ mechanic }: BlockOf<"appointee">) {
  return (
    <MechanicBlock
      title="Seu partido"
      description="A renda do Comissionado acompanha o partido no governo"
      links={[{ label: "Eleição", to: "/election" }]}
    >
      <BlockPanel title={mechanic.party ?? "Sem partido"} aside={<MetricHint metric={PARTY_MULTIPLE} />}>
        <KeyValueRow
          label="Renda hoje"
          note={mechanic.in_government ? "o partido está no governo" : "o partido está fora do governo"}
          value={`${multiple(mechanic.multiple_now)} o salário`}
        />
        <KeyValueRow
          label="Se o partido perder"
          note="a renda cai de patamar"
          value={`${multiple(mechanic.multiple_outside)} o salário`}
        />
        <KeyValueRow
          label="Com o partido no governo"
          value={`${multiple(mechanic.multiple_in_government)} o salário`}
        />
        {mechanic.election_in_months !== null && (
          <KeyValueRow label="Próxima eleição" value={electionIn(mechanic.election_in_months)} />
        )}
      </BlockPanel>
    </MechanicBlock>
  );
}

/** O que o Banqueiro de ofertas tem no lugar de uma mecânica: as comissões das ofertas. */
export function OffersBankerBlock({ mechanic }: BlockOf<"offers_banker">) {
  return (
    <MechanicBlock
      title="Suas comissões"
      description="Você ganha uma comissão sobre as ofertas de cotas que os fundos fecham"
      links={[{ label: "Ofertas", to: "/offers" }]}
    >
      <BlockPanel title="Comissões">
        <KeyValueRow
          label="Comissão do mês"
          note={`${mechanic.month_offers} ${mechanic.month_offers === 1 ? "oferta" : "ofertas"}`}
          value={displayMoney(mechanic.month_commission)}
        />
        <KeyValueRow
          label="Comissão no total"
          note={`${mechanic.total_offers} ${mechanic.total_offers === 1 ? "oferta" : "ofertas"}`}
          value={displayMoney(mechanic.total_commission)}
        />
      </BlockPanel>
    </MechanicBlock>
  );
}
