import { afterEach, describe, expect, it, vi } from "vitest";
import { DropdownMenuItem } from "@/shared/components/ui/dropdown-menu";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { selectFund } from "@/shared/lib/active-account";
import { queryClient } from "@/shared/lib/queryClient";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { FundAccount } from "@/types";
import { AccountMenu } from "./account-menu";
import { click, findElements } from "./element-tree";

// O menu só lê o apelido do jogador para a sigla da conta pessoal
vi.mock("@/shared/hooks/useAuth", () => ({ useAuth: () => ({ user: { nickname: "Lilo" } }) }));

const personal: FundAccount = {
  fund_id: null,
  name: "Conta pessoal",
  ticker: null,
  cash: "1000.00",
  frozen_until: null,
};
const aurora: FundAccount = {
  fund_id: 3,
  name: "Aurora Gestão",
  ticker: "AURO11",
  cash: "96300.00",
  frozen_until: null,
};

// Partida própria deste arquivo: o estado do módulo é compartilhado entre os testes
const SIMULATION = 9002;

afterEach(() => {
  selectFund(SIMULATION, null);
  queryClient.clear();
  vi.unstubAllGlobals();
});

const sentHeaders = async () => {
  const fetch = vi.fn().mockResolvedValue(new Response(null, { status: 204 }));
  vi.stubGlobal("fetch", fetch);
  await apiFetch("/api/variable-income/ABCD3/orders", { method: "POST", body: {}, activeAccount: true });
  const init = fetch.mock.calls[0]?.[1] as RequestInit;
  return init.headers as Record<string, string>;
};

describe("menu Operar com", () => {
  it("escolher a gestora no menu faz as próximas chamadas de mercado levarem X-Account", async () => {
    queryClient.setQueryData(queryKeys.simulationStatus(), { simulation: { id: SIMULATION, funds_enabled: true } });
    const onSelect = vi.fn((fundId: number | null) => selectFund(SIMULATION, fundId));
    const tree = AccountMenu({ accounts: [personal, aurora], active: personal, onSelect });
    const items = findElements(tree, (element) => element.type === DropdownMenuItem);

    expect(items).toHaveLength(2);
    expect(await sentHeaders()).not.toHaveProperty("X-Account");

    click(items[1]);
    expect(onSelect).toHaveBeenCalledWith(3);
    expect(await sentHeaders()).toMatchObject({ "X-Account": "3" });

    // Voltar para a pessoal tira o cabeçalho
    click(items[0]);
    expect(await sentHeaders()).not.toHaveProperty("X-Account");
  });

  it("sem a expansão Gestoras a escolha lembrada não vai no cabeçalho", async () => {
    queryClient.setQueryData(queryKeys.simulationStatus(), { simulation: { id: SIMULATION, funds_enabled: false } });
    selectFund(SIMULATION, 3);
    expect(await sentHeaders()).not.toHaveProperty("X-Account");
  });

  it("marca a conta em uso e mostra o caixa de cada uma", () => {
    const tree = AccountMenu({ accounts: [personal, aurora], active: aurora, onSelect: vi.fn() });
    const variants = findElements(tree, (element) => element.type === DropdownMenuItem).map(
      (element) => element.props["variant"],
    );

    expect(variants).toEqual(["default", "fund"]);
  });
});
