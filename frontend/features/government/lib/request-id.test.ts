import { describe, expect, it, vi } from "vitest";
import { governmentRequestId } from "./request-id";

describe("identificador de comandos políticos na rede local", () => {
  it("gera UUIDs diferentes mesmo sem crypto.randomUUID no HTTP", () => {
    const original = globalThis.crypto;
    vi.stubGlobal("crypto", { getRandomValues: original.getRandomValues.bind(original) });
    try {
      const first = governmentRequestId();
      const second = governmentRequestId();
      expect(first).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/);
      expect(first).not.toBe(second);
    } finally {
      vi.unstubAllGlobals();
    }
  });
});
