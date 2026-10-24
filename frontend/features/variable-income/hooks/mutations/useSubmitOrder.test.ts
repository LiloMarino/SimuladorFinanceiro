import { beforeEach, describe, expect, it, vi } from "vitest";
import { toast } from "sonner";
import { notifyExecution } from "./useSubmitOrder";

vi.mock("sonner", () => ({ toast: { info: vi.fn() } }));

// O Intl separa o R$ do número com espaço não separável
const lastMessage = () => (vi.mocked(toast.info).mock.calls[0][0] as string).replace(/\s/g, " ");

const response = (quantity: string, total: string) => ({ order_id: "a", status: "EXECUTED", quantity, total });

describe("aviso depois da compra a mercado", () => {
  beforeEach(() => vi.mocked(toast.info).mockClear());

  it("por quantidade, avisa quando saiu menos que o pedido, com o preço que valeu", () => {
    notifyExecution("PETR4", { type: "market", action: "buy", quantity: "568" }, response("541", "18404.82"));
    expect(lastMessage()).toContain("Comprou 541 de 568 PETR4: o preço subiu para R$ 34,02");
  });

  it("por quantidade, fica quieto quando saiu o que foi pedido", () => {
    notifyExecution("PETR4", { type: "market", action: "buy", quantity: "568" }, response("568", "18403.20"));
    expect(toast.info).not.toHaveBeenCalled();
  });

  it("por valor, avisa sempre, com o total gasto e o que sobrou", () => {
    notifyExecution("PETR4", { type: "market", action: "buy", amount: "18420.35" }, response("567", "18411.00"));
    expect(lastMessage()).toContain("Comprou 567 PETR4 por R$ 18.411,00 · sobraram R$ 9,35");
  });
});
