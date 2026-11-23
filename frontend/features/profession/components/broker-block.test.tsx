import { renderToStaticMarkup } from "react-dom/server";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import type { ProfessionMechanic } from "@/types";
import { BrokerBlock } from "./broker-block";

type Broker = Extract<ProfessionMechanic, { kind: "broker" }>;
type Report = NonNullable<Broker["current"]>;
type Item = Report["items"][number];

const item = (partial: Partial<Item>): Item => ({
  id: 1,
  report_month: "2012-03-01",
  issued_on: "2012-03-07",
  ticker: "PETR4",
  side: "buy",
  price: "30.00",
  target: "34.50",
  deadline: "2012-06-29",
  result: null,
  result_price: null,
  resolved_on: null,
  ...partial,
});

const current: Report = {
  month: "2012-03-01",
  issued_on: "2012-03-07",
  items: [item({}), item({ id: 2, ticker: "VALE3", side: "sell", price: "52.10", target: "47.00" })],
};

const previous: Report = {
  month: "2012-02-01",
  issued_on: "2012-02-07",
  items: [
    item({ id: 3, report_month: "2012-02-01", ticker: "ITUB4", target: "33.40", result: "hit", result_price: "33.40" }),
    item({
      id: 4,
      report_month: "2012-02-01",
      ticker: "BBDC4",
      side: "sell",
      target: "17.00",
      result: "miss",
      result_price: "18.90",
    }),
    item({ id: 5, report_month: "2012-02-01", ticker: "ABEV3", deadline: "2012-05-31" }),
  ],
};

const mechanic = (partial: Partial<Broker>): Broker => ({
  kind: "broker",
  status: "ACTIVE",
  current,
  previous,
  next_report_on: "2012-04-05",
  hits: 14,
  resolved: 22,
  hit_rate: "0.6364",
  income: "9100.00",
  fixed_income: "5600.00",
  commission: "3500.00",
  commission_rate: "0.0005",
  volume: "12400000.00",
  brokers: 2,
  capped: false,
  ...partial,
});

function render(broker: Broker) {
  // O formatador de moeda separa o R$ do valor com espaço sem quebra
  return renderToStaticMarkup(
    <MemoryRouter>
      <BrokerBlock mechanic={broker} />
    </MemoryRouter>,
  ).replaceAll(" ", " ");
}

describe("BrokerBlock", () => {
  it("com relatório, mostra o placar, a renda, a comissão e as duas tabelas", () => {
    const html = render(mechanic({}));
    expect(html).toContain("Sua mecânica: relatório da casa");
    expect(html).toContain("Ativo");
    expect(html).toContain(
      "A corretora manda as recomendações de março dias antes das notícias. Acerta mais que o acaso, mas erra.",
    );
    expect(html).toContain("Abrir na Renda variável");
    expect(html).toContain("Acertou 14 de 22 (64%)");
    expect(html).toContain("só conta recomendação com o prazo vencido · o acaso daria 50%");
    expect(html).toContain("R$ 9.100,00");
    expect(html).toContain("fixo R$ 5.600,00 + comissão R$ 3.500,00");
    expect(html).toContain("0,05% dos R$ 12,4 mi negociados na sala, ÷ 2 corretores");
    expect(html).not.toContain("teto de 1× o fixo");
    expect(html).toContain("Relatório de março · recebido em 07 mar 2012");
    expect(html).toContain("PETR4");
    expect(html).toContain("Compra");
    expect(html).toContain("R$ 34,50");
    expect(html).toContain("jun 2012");
    expect(html).toContain("Venda");
    expect(html).toContain("Relatório de fevereiro · o que acertou");
    expect(html).toContain("Fev 2012");
    expect(html).toContain("Acertou");
    expect(html).toContain("chegou a R$ 33,40");
    expect(html).toContain("Errou");
    expect(html).toContain("fechou o prazo em R$ 18,90");
    expect(html).toContain("Em aberto");
    expect(html).toContain("prazo até mai 2012");
    expect(html).toContain("Renda variável, ação com o selo do relatório");
  });

  it("com o teto atingido, a nota da comissão diz que o teto cortou", () => {
    const html = render(mechanic({ capped: true }));
    expect(html).toContain("limitada ao teto de 1× o fixo");
  });

  it("sem recomendação vencida, o placar não inventa um percentual", () => {
    const html = render(mechanic({ hits: 0, resolved: 0, hit_rate: null, previous: null }));
    expect(html).not.toContain("Acertou 0 de 0");
    expect(html).not.toContain("o que acertou");
  });

  it("antes do primeiro relatório, diz quando ele chega e a renda é só o fixo", () => {
    const html = render(
      mechanic({
        status: "AVAILABLE",
        current: null,
        previous: null,
        hits: 0,
        resolved: 0,
        hit_rate: null,
        income: "5600.00",
        fixed_income: "5600.00",
        commission: "0.00",
        volume: "0.00",
      }),
    );
    expect(html).toContain("Disponível");
    expect(html).toContain("O primeiro relatório chega no 5º dia útil do mês.");
    expect(html).toContain("Ainda sem relatório.");
    expect(html).toContain("O de abril chega em 05 abr 2012, com 3 a 5 ações.");
    expect(html).toContain("O placar começa quando o prazo da primeira recomendação vencer.");
    expect(html).toContain("só o fixo: a sala ainda não negociou nada");
    expect(html).toContain("R$ 5.600,00");
    expect(html).not.toContain("Abrir na Renda variável");
    expect(html).not.toContain("Placar da casa");
  });
});
