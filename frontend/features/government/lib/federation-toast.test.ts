import { describe, expect, it } from "vitest";
import type { GovernmentNotice } from "@/types";
import { federationAnsweredToast, federationLeftToast, federationProposedToast } from "./federation-toast";

const notice = (overrides: Partial<GovernmentNotice>) => ({ ...overrides }) as GovernmentNotice;

describe("federationProposedToast", () => {
  it("diz quem propõe, a quem e até quando responder", () => {
    expect(
      federationProposedToast(notice({ party_abbr: "RPV", partner_abbr: "PTD", effective: "2027-03-21" })),
    ).toEqual({
      tone: "info",
      title: "O RPV propõe federação ao PTD",
      description: "Responda até 21 mar; sem resposta, a proposta expira.",
    });
  });
});

describe("federationAnsweredToast", () => {
  it("conta a formação com a data final", () => {
    const toast = federationAnsweredToast(
      notice({ party_abbr: "NOV", federation_name: "Federação PTD–NOV", accepted: true, effective: "2031-12-31" }),
    );

    expect(toast.tone).toBe("success");
    expect(toast.description).toBe("Federação PTD–NOV formada. Vale até 31 dez 2031.");
  });

  it("avisa a recusa", () => {
    const toast = federationAnsweredToast(
      notice({ party_abbr: "NOV", federation_name: "Federação PTD–NOV", accepted: false }),
    );

    expect(toast).toEqual({
      tone: "warning",
      title: "O NOV recusou a federação",
      description: "A proposta da Federação PTD–NOV foi recusada.",
    });
  });
});

describe("federationLeftToast", () => {
  it("diz quem saiu e que a federação acabou para os dois", () => {
    expect(federationLeftToast(notice({ party_abbr: "NOV", federation_name: "Federação PTD–NOV" })).title).toBe(
      "O NOV deixou a federação",
    );
  });
});
