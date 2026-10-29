import { describe, expect, it } from "vitest";
import {
  blocColor,
  causeLabel,
  outlook,
  outlookLabel,
  partySeats,
  rangeLabel,
  resultLabel,
  seatChange,
  shareOfVotes,
  unguidedCount,
  voteSeats,
  type Bloc,
  type Vote,
} from "./house";

const bloc = (overrides: Partial<Bloc>): Bloc => ({
  key: 1,
  party_id: 1,
  abbr: "PRL",
  name: "Partido",
  color: "#15803D",
  is_computer: false,
  votes: "25",
  seats: 3,
  previous_seats: null,
  governing: false,
  votes_cast: 0,
  yes_share: null,
  defection_share: null,
  is_mine: false,
  ...overrides,
});

const blocVote = (overrides: Partial<Vote["blocs"][number]>): Vote["blocs"][number] => ({
  key: 1,
  abbr: "PRL",
  color: "#15803D",
  seats: 4,
  orientation: true,
  guided: false,
  may_defect: 1,
  yes: null,
  no: null,
  defected: null,
  cause: null,
  cause_share: null,
  by_deal: false,
  ...overrides,
});

const vote = (blocs: Vote["blocs"], overrides: Partial<Vote> = {}): Vote => ({
  blocs,
  needed: 51,
  yes: null,
  no: null,
  defected: null,
  low: null,
  high: null,
  guide: null,
  ...overrides,
});

describe("rangeLabel", () => {
  it("mostra a faixa, ou um número só quando ela fecha", () => {
    expect(rangeLabel(53, 60)).toBe("53 a 60");
    expect(rangeLabel(55, 55)).toBe("55");
    expect(rangeLabel(null, null)).toBe("—");
  });
});

describe("outlook", () => {
  it("passa quando a faixa toda está em 51 ou mais", () => {
    expect(outlook({ low: 53, high: 60, needed: 51 })).toBe("passes");
    expect(outlookLabel({ low: 53, high: 60, needed: 51 })).toBe("Passa com 53 a 60");
  });

  it("cai quando a faixa toda está abaixo", () => {
    expect(outlook({ low: 40, high: 46, needed: 51 })).toBe("falls");
    expect(outlookLabel({ low: 40, high: 46, needed: 51 })).toBe("Cai com 40 a 46");
  });

  it("fica aberta quando a faixa cruza a linha", () => {
    expect(outlook({ low: 47, high: 55, needed: 51 })).toBe("open");
  });

  it("passa com exatamente 51 e cai com 50", () => {
    expect(outlook({ low: 51, high: 51, needed: 51 })).toBe("passes");
    expect(outlook({ low: 50, high: 50, needed: 51 })).toBe("falls");
  });
});

describe("resultLabel", () => {
  it("põe o lado vencedor primeiro", () => {
    expect(resultLabel({ yes: 54, no: 47 }, true)).toBe("Aprovada por 54 a 47");
    expect(resultLabel({ yes: 44, no: 57 }, false)).toBe("Rejeitada por 57 a 44");
  });
});

describe("seatChange", () => {
  it("assina a mudança e some na primeira casa", () => {
    expect(seatChange({ seats: 33, previous_seats: 27 })).toBe("+6");
    expect(seatChange({ seats: 28, previous_seats: 31 })).toBe("-3");
    expect(seatChange({ seats: 11, previous_seats: 11 })).toBe("0");
    expect(seatChange({ seats: 11, previous_seats: null })).toBeNull();
  });
});

describe("blocColor", () => {
  it("usa a cor do partido de jogador e a paleta fixa no do computador", () => {
    expect(blocColor({ abbr: "PRL", color: "#15803D" })).toBe("#15803D");
    expect(blocColor({ abbr: "UPR", color: null })).toBe("#7D879B");
    expect(blocColor({ abbr: "ACI", color: null })).toBe("#0369A1");
  });
});

describe("causeLabel", () => {
  it("diz que grupo da bancada quer o voto contrário", () => {
    const text = causeLabel({ abbr: "MRC", cause: "INVESTORS", cause_share: "0.4", orientation: true }, "a medida");
    expect(text).toContain("40% dos eleitores do MRC");
    expect(text).toContain("rejeitam a medida");
  });

  it("não inventa causa quando ninguém quer o voto contrário", () => {
    expect(causeLabel({ abbr: "MRC", cause: null, cause_share: null, orientation: true }, "a medida")).toBeNull();
  });
});

describe("shareOfVotes", () => {
  it("vem sempre com o tamanho da amostra", () => {
    expect(shareOfVotes("75", 8)).toBe("75% de 8");
    expect(shareOfVotes(null, 0)).toBe("—");
  });
});

describe("partySeats", () => {
  it("preenche as 101 cadeiras, deixando vazias as que faltam", () => {
    const seats = partySeats([bloc({ seats: 3 })]);
    expect(seats).toHaveLength(101);
    expect(seats.filter((seat) => seat.tone === "solid")).toHaveLength(3);
    expect(seats.filter((seat) => seat.tone === "empty")).toHaveLength(98);
  });
});

describe("voteSeats", () => {
  it("antes da votação, enche a bancada que orienta Sim e põe anel em quem pode desobedecer", () => {
    const seats = voteSeats(vote([blocVote({ seats: 4, orientation: true, may_defect: 1 })]));
    expect(seats.slice(0, 4).map((seat) => seat.tone)).toEqual(["solid", "solid", "solid", "solid"]);
    expect(seats.slice(0, 4).map((seat) => seat.ring)).toEqual([false, false, false, true]);
  });

  it("depois da votação, enche quem votou Sim e põe anel em quem votou contra o líder", () => {
    const seats = voteSeats(vote([blocVote({ seats: 4, orientation: true, yes: 3, no: 1, defected: 1 })]));
    expect(seats.slice(0, 4).map((seat) => seat.tone)).toEqual(["solid", "solid", "solid", "light"]);
    expect(seats.filter((seat) => seat.ring)).toHaveLength(1);
  });
});

describe("unguidedCount", () => {
  const guide = { bloc_key: 1 } as NonNullable<Vote["guide"]>;
  const queue = (guided: boolean) =>
    [{ vote: vote([blocVote({ key: 1, guided })], { guide }) }] as Parameters<typeof unguidedCount>[1];

  it("conta a votação em que o líder ainda não orientou", () => {
    expect(unguidedCount({ impeachment_request: null } as Parameters<typeof unguidedCount>[0], queue(false))).toBe(1);
  });

  it("não conta a que ele já orientou", () => {
    expect(unguidedCount({ impeachment_request: null } as Parameters<typeof unguidedCount>[0], queue(true))).toBe(0);
  });
});
