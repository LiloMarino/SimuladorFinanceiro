import { describe, expect, it } from "vitest";
import type { BaseBloc, BaseDeal } from "@/types";
import {
  baseOutlook,
  baseSeats,
  blocStatus,
  daysLeftLabel,
  groupsLabel,
  majorityMargin,
  outsideLabel,
  pendingLabel,
  yearShare,
} from "./base";

const bloc = (overrides: Partial<BaseBloc>): BaseBloc => ({
  key: 1,
  party_id: 1,
  abbr: "PRL",
  name: "Partido",
  color: "#15803D",
  seats: 4,
  is_computer: false,
  centrao: false,
  leader: "Lilo",
  governing: false,
  in_base: false,
  pending: false,
  ratio: "0.0002",
  monthly: "1000000",
  blocker: null,
  retry_from: null,
  declined_on: null,
  ...overrides,
});

describe("majorityMargin", () => {
  it("conta a folga acima da maioria", () => {
    expect(majorityMargin(57, 51)).toEqual({ text: "6 de folga sobre a maioria", enough: true });
  });

  it("conta quantas cadeiras faltam", () => {
    expect(majorityMargin(33, 51)).toEqual({ text: "faltam 18 cadeiras para a maioria", enough: false });
    expect(majorityMargin(50, 51).text).toBe("faltam 1 cadeira para a maioria");
  });
});

describe("daysLeftLabel", () => {
  it("usa dias até dois meses e meses depois", () => {
    expect(daysLeftLabel(1)).toBe("falta 1 dia");
    expect(daysLeftLabel(45)).toBe("faltam 45 dias");
    expect(daysLeftLabel(150)).toBe("faltam 5 meses");
  });
});

describe("groupsLabel", () => {
  it("junta os grupos com o primeiro em maiúscula", () => {
    expect(groupsLabel(["RETIREES", "PUBLIC_SERVANTS"]).toLowerCase()).toContain(" e ");
  });
});

describe("yearShare", () => {
  it("mostra a fração do PIB em percentual", () => {
    expect(yearShare("0.0011")).toBe("0,11%");
  });
});

describe("blocStatus", () => {
  it("separa governo, base, espera e fora", () => {
    expect(blocStatus(bloc({ governing: true }))).toBe("governing");
    expect(blocStatus(bloc({ in_base: true }))).toBe("in_base");
    expect(blocStatus(bloc({ pending: true }))).toBe("pending");
    expect(blocStatus(bloc({}))).toBe("outside");
  });
});

describe("baseSeats", () => {
  it("enche a base, clareia quem está fora e põe anel na escolhida", () => {
    const blocs = [bloc({ key: 1, governing: true, seats: 3 }), bloc({ key: 2, seats: 2 })];
    const seats = baseSeats(blocs, 2).filter((seat) => seat.blocKey !== undefined);
    expect(seats.filter((seat) => seat.blocKey === 1).every((seat) => seat.tone === "solid")).toBe(true);
    expect(seats.filter((seat) => seat.blocKey === 2).every((seat) => seat.ring)).toBe(true);
    expect(
      baseSeats(blocs)
        .filter((seat) => seat.blocKey === 2)
        .every((seat) => seat.tone === "light"),
    ).toBe(true);
  });
});

describe("outsideLabel", () => {
  it("lista quem está fora com o líder e as cadeiras", () => {
    const blocs = [
      bloc({ governing: true }),
      bloc({ abbr: "MRC", leader: "Rafa", seats: 16 }),
      bloc({ abbr: "ACI", leader: null, seats: 11, in_base: true }),
    ];
    expect(outsideLabel(blocs)).toBe("MRC (Rafa, 16)");
  });
});

describe("baseOutlook", () => {
  it("compara a base com a maioria e os dois terços", () => {
    expect(baseOutlook(74, 51, 68)).toBe("passa dos dois terços (68)");
    expect(baseOutlook(57, 51, 68)).toBe("passa da maioria (51)");
    expect(baseOutlook(46, 51, 68)).toBe("segue abaixo da maioria (51)");
  });
});

describe("pendingLabel", () => {
  it("diz quem responde e até quando", () => {
    const deal = { abbr: "PRL", leader: "Lilo", answer_by: "2023-03-29" } as BaseDeal;
    expect(pendingLabel(deal)).toContain("aguardando Lilo");
    expect(pendingLabel({ ...deal, answer_by: null, leader: null })).toBe("PRL responde no próximo pregão");
  });
});
