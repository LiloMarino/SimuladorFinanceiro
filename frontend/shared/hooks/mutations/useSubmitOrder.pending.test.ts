import { MutationObserver, QueryClient, QueryObserver } from "@tanstack/react-query";
import { describe, expect, it, vi } from "vitest";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useSubmitOrder } from "./useSubmitOrder";

const client = new QueryClient();

// O useMutation devolve as próprias opções, para o MutationObserver rodar a mutation sem React
vi.mock("@tanstack/react-query", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@tanstack/react-query")>()),
  useMutation: (options: unknown) => options,
  useQueryClient: () => client,
}));
vi.mock("@/shared/lib/api/apiFetch", () => ({
  apiFetch: () => Promise.resolve({ order_id: "a", status: "OPEN", quantity: "0", total: "0" }),
}));
vi.mock("@/shared/notifications/toast-api-error", () => ({ toastApiError: vi.fn() }));
vi.mock("sonner", () => ({ toast: { info: vi.fn() } }));

describe("envio da ordem", () => {
  it("libera a mutation quando o servidor confirma, com a releitura ainda em andamento", async () => {
    const refetchStarted = vi.fn();
    // Uma query ativa cuja releitura nunca termina
    const query = new QueryObserver(client, {
      initialData: "anterior",
      queryKey: queryKeys.orderPreview("PETR4"),
      queryFn: () => {
        refetchStarted();
        return new Promise(() => undefined);
      },
    });
    const unsubscribe = query.subscribe(() => undefined);
    refetchStarted.mockClear();

    const options = useSubmitOrder("PETR4") as unknown as ConstructorParameters<typeof MutationObserver>[1];
    const mutation = new MutationObserver(client, options);
    await expect(
      mutation.mutate({ action: "buy", type: "limit", quantity: "1", limit_price: 10 }),
    ).resolves.toBeDefined();

    expect(mutation.getCurrentResult().isPending).toBe(false);
    await vi.waitFor(() => expect(refetchStarted).toHaveBeenCalled());
    unsubscribe();
  });
});
