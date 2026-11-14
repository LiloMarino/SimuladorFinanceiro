import { describe, expect, it } from "vitest";
import { RANDOM_STRATEGY } from "@/shared/lib/bot-form";
import type { StrategyInfo } from "@/types";
import { batchRequests } from "./bot-form";

const strategy = (key: string, bot_names: string[]) =>
  ({ key, name: key, bot_names, params: [] }) as unknown as StrategyInfo;

const hold = strategy("buy_and_hold", ["Tio Patinhas", "Paciência"]);
const rsi = strategy("rsi", ["Gatilho"]);

describe("batchRequests", () => {
  it("dá nomes diferentes aos bots do lote, fora dos que a sala já tem", () => {
    const requests = batchRequests([hold], ["tio patinhas"], {
      strategyKey: "buy_and_hold",
      params: {},
      quantity: 3,
      profession: null,
    });

    const names = requests.map((r) => r.nickname);
    expect(names).toHaveLength(3);
    expect(new Set(names.map((n) => n.toLowerCase())).size).toBe(3);
    expect(names).not.toContain("Tio Patinhas");
    // A lista da estratégia acaba no segundo bot: o terceiro vira "<estratégia> #2"
    expect(names).toContain("buy_and_hold #2");
  });

  it("leva os parâmetros do formulário quando a estratégia é escolhida", () => {
    const requests = batchRequests([hold, rsi], [], {
      strategyKey: "rsi",
      params: { period: 7 },
      quantity: 2,
      profession: null,
    });

    expect(requests.map((r) => [r.strategy_key, r.params])).toEqual([
      ["rsi", { period: 7 }],
      ["rsi", { period: 7 }],
    ]);
  });

  it("sorteia a estratégia de cada bot no catálogo, com os parâmetros padrão", () => {
    // Cada bot gasta dois sorteios: a estratégia (0 → 1ª, 0,99 → última) e depois o nome
    const draws = [0, 0, 0.99, 0];
    const requests = batchRequests(
      [hold, rsi],
      [],
      { strategyKey: RANDOM_STRATEGY, params: { period: 7 }, quantity: 2, profession: null },
      () => draws.shift() ?? 0,
    );

    expect(requests.map((r) => r.strategy_key)).toEqual(["buy_and_hold", "rsi"]);
    expect(requests.every((r) => Object.keys(r.params ?? {}).length === 0)).toBe(true);
  });

  it("deixa cor e equipe para o servidor", () => {
    const [request] = batchRequests([hold], [], {
      strategyKey: "buy_and_hold",
      params: {},
      quantity: 1,
      profession: null,
    });

    expect(request).not.toHaveProperty("color");
    expect(request).not.toHaveProperty("team");
  });

  it("leva a profissão escolhida a todos os bots do lote", () => {
    const requests = batchRequests([hold], [], {
      strategyKey: "buy_and_hold",
      params: {},
      quantity: 3,
      profession: "BANKER",
    });

    expect(requests.map((r) => r.profession)).toEqual(["BANKER", "BANKER", "BANKER"]);
  });

  it("deixa a profissão nula para o servidor sortear uma por bot", () => {
    const requests = batchRequests([hold], [], {
      strategyKey: "buy_and_hold",
      params: {},
      quantity: 2,
      profession: null,
    });

    expect(requests.map((r) => r.profession)).toEqual([null, null]);
  });
});
