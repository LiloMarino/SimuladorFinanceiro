import { describe, expect, it } from "vitest";
import ApiError from "@/shared/lib/models/ApiError";
import { creditLockOfAccount, creditLockOfError } from "./credit-lock";

describe("creditLockOfAccount", () => {
  it("trava o Fundo Soberano e o co-gestor", () => {
    expect(creditLockOfAccount({ role: "president" })).toBe("sovereign");
    expect(creditLockOfAccount({ role: "comanager" })).toBe("comanager");
  });

  it("libera a conta pessoal, o gestor principal e a lista ainda não carregada", () => {
    expect(creditLockOfAccount({ role: null })).toBeNull();
    expect(creditLockOfAccount({ role: "manager" })).toBeNull();
    expect(creditLockOfAccount(undefined)).toBeNull();
  });
});

describe("creditLockOfError", () => {
  const forbidden = (code: string | undefined) => new ApiError("Proibido", 403, code === undefined ? {} : { code });

  it("lê o motivo tipado do 403", () => {
    expect(creditLockOfError(forbidden("credit_sovereign_fund"))).toBe("sovereign");
    expect(creditLockOfError(forbidden("credit_comanager"))).toBe("comanager");
  });

  it("ignora erro sem motivo conhecido", () => {
    expect(creditLockOfError(forbidden("outro"))).toBeNull();
    expect(creditLockOfError(forbidden(undefined))).toBeNull();
    expect(creditLockOfError(null)).toBeNull();
  });
});
