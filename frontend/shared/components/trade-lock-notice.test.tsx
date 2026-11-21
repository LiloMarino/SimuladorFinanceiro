import { QueryClientProvider } from "@tanstack/react-query";
import type { ReactElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { afterEach, describe, expect, it, vi } from "vitest";
import { click, findElements } from "@/layouts/partial/element-tree";
import { Button } from "@/shared/components/ui/button";
import { queryClient } from "@/shared/lib/queryClient";
import type { FundAccount } from "@/types";
import { TradeLockNotice } from "./trade-lock-notice";

const personal: FundAccount = {
  fund_id: null,
  name: "Conta pessoal",
  ticker: null,
  cash: "1000.00",
  frozen_until: null,
  automatic: false,
  eliminated_on: null,
  role: null,
};
const aurora: FundAccount = {
  fund_id: 3,
  name: "Aurora Gestão",
  ticker: "AURO11",
  cash: "96300.00",
  frozen_until: null,
  automatic: true,
  eliminated_on: null,
  role: "manager",
};

// A conta no topo é a que o teste escolhe; o resto do hook (partida, lista de contas) não entra na conta
const topAccount = vi.hoisted(() => ({ current: undefined as unknown }));
vi.mock("@/shared/hooks/useActiveAccount", () => ({ useActiveAccount: () => ({ active: topAccount.current }) }));

afterEach(() => {
  queryClient.clear();
  vi.unstubAllGlobals();
});

/** Renderiza o aviso com a conta escolhida e devolve a árvore dele, como o jogador a vê. */
function renderNotice(account: FundAccount, lock: Parameters<typeof TradeLockNotice>[0]["lock"]) {
  topAccount.current = account;

  let tree: ReactElement | null = null;
  function Probe() {
    tree = TradeLockNotice({ lock });
    return null;
  }
  renderToStaticMarkup(
    <QueryClientProvider client={queryClient}>
      <Probe />
    </QueryClientProvider>,
  );
  return tree;
}

const turnOffRequest = async (account: FundAccount, lock: Parameters<typeof TradeLockNotice>[0]["lock"]) => {
  const fetch = vi.fn().mockResolvedValue(new Response(null, { status: 204 }));
  vi.stubGlobal("fetch", fetch);
  const tree = renderNotice(account, lock);

  click(findElements(tree, (element) => element.type === Button)[0]);

  await vi.waitFor(() => expect(fetch).toHaveBeenCalled());
  const [url, init] = fetch.mock.calls[0] as [string, RequestInit];
  return { url, method: init.method, body: typeof init.body === "string" ? (JSON.parse(init.body) as unknown) : null };
};

describe("aviso de boleta travada pelo automático", () => {
  it("na gestora o botão desliga o automático da gestora", async () => {
    const request = await turnOffRequest(aurora, { reason: "fund-automatic", name: aurora.name, until: null });

    expect(request).toEqual({ url: "/api/funds/3/strategy", method: "PUT", body: { key: null, params: {} } });
  });

  it("na conta pessoal o botão desliga o automático pessoal", async () => {
    const request = await turnOffRequest(personal, { reason: "automatic" });

    expect(request).toEqual({ url: "/api/strategies/me", method: "PUT", body: { key: null, params: {} } });
  });
});
