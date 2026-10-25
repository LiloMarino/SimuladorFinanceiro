import type { OrderPreviewRequest } from "@/types";
import { fakeOrderPreview } from "./fake-order-preview";

const PREVIEW_PATH = /^\/api\/variable-income\/[^/]+\/order-preview$/;
const LATENCY_MS = 150;

const json = (body: unknown) =>
  new Response(JSON.stringify(body), { status: 200, headers: { "Content-Type": "application/json" } });

const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

const pathOf = (input: RequestInfo | URL) =>
  typeof input === "string" ? input : input instanceof URL ? input.pathname : new URL(input.url).pathname;

/**
 * Responde só a prévia da ordem do palco; qualquer outra chamada segue
 * para a rede. Devolve a função que restaura o `fetch` original.
 */
export function installStageFetch() {
  const original = window.fetch;

  window.fetch = async (input, init) => {
    const path = pathOf(input);
    if (PREVIEW_PATH.test(path) && typeof init?.body === "string") {
      await wait(LATENCY_MS);
      return json(fakeOrderPreview(JSON.parse(init.body) as OrderPreviewRequest));
    }
    return original(input, init);
  };

  return () => {
    window.fetch = original;
  };
}
