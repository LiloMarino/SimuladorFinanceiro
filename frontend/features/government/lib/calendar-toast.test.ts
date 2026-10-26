import { describe, expect, it } from "vitest";
import type { GovernmentNotice } from "@/types";
import { calendarToast } from "./calendar-toast";

const notice = (kind: GovernmentNotice["kind"]) =>
  ({ kind, ticket_deadline: "2021-09-30", first_round: "2021-10-07" }) as GovernmentNotice;

describe("calendarToast", () => {
  it("avisa a data em que as chapas fecham", () => {
    const toast = calendarToast(notice("TICKETS_CLOSING"));
    expect(toast?.tone).toBe("warning");
    expect(toast?.title).toBe("As chapas fecham em 30 set");
  });

  it("avisa a data do 1º turno na véspera", () => {
    expect(calendarToast(notice("ELECTION_EVE"))?.title).toBe("O 1º turno é em 07 out");
  });

  it("ignora o aviso sem as datas do calendário", () => {
    expect(calendarToast({ kind: "TICKETS_CLOSING" })).toBeNull();
    expect(calendarToast(notice("UPDATED"))).toBeNull();
  });
});
