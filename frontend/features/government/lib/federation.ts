import type { ElectionParty, Federation, FederationRejection } from "@/types";

export type FederationCandidate = {
  /** Identifica a opção na lista: partido e apelido, vazio no candidato do computador */
  key: string;
  partyId: number;
  /** Nulo no candidato do computador */
  nickname: string | null;
  label: string;
  abbr: string;
};

/** Quem pode ser o candidato da chapa: os filiados de cada partido, ou o candidato do computador. */
export function federationCandidates(own: ElectionParty, partner: ElectionParty): FederationCandidate[] {
  return [own, partner].flatMap((party): FederationCandidate[] => {
    if (party.is_computer) {
      return [
        {
          key: `${party.id}:`,
          partyId: party.id,
          nickname: null,
          label: party.candidate?.name ?? `Candidato do ${party.abbr}`,
          abbr: party.abbr,
        },
      ];
    }
    const current = party.candidate?.nickname;
    return [...party.members]
      .sort((a, b) => Number(b.nickname === current) - Number(a.nickname === current))
      .map((member) => ({
        key: `${party.id}:${member.nickname}`,
        partyId: party.id,
        nickname: member.nickname,
        label: member.nickname,
        abbr: party.abbr,
      }));
  });
}

/** O quanto a rejeição sobe com a federação, em pontos inteiros com sinal ("+6"); vazio quando não muda. */
export function rejectionDelta(row: Pick<FederationRejection, "own" | "federated">) {
  const points = Math.round(Number(row.federated)) - Math.round(Number(row.own));
  if (points === 0) return "";
  return `${points > 0 ? "+" : "−"}${Math.abs(points)}`;
}

/** A federação em que o partido está, se estiver. */
export function federationOf(federations: Federation[], partyId: number) {
  return federations.find((federation) => federation.parties.includes(partyId));
}

/** O outro partido da federação. */
export function partnerOf(federation: Federation, partyId: number) {
  return federation.parties.find((id) => id !== partyId);
}

/** A federação que disputa a eleição do ano dado, se o partido estiver numa. */
export function raceFederationOf(federations: Federation[], year: number, partyId: number) {
  return federations.find((federation) => federation.election_year === year && federation.parties.includes(partyId));
}

export type RaceRow = {
  key: string;
  /** Os partidos da linha: um só, ou os dois da federação com o do candidato primeiro */
  parties: ElectionParty[];
  federation: Federation | null;
};

/** As linhas da corrida: um partido por linha, e os dois da federação juntos na posição do primeiro que aparece. */
export function raceRows(parties: ElectionParty[], federations: Federation[], year: number): RaceRow[] {
  const placed = new Set<number>();
  const rows: RaceRow[] = [];
  for (const party of parties) {
    if (placed.has(party.id)) continue;
    const federation = raceFederationOf(federations, year, party.id);
    const members = federation
      ? [...federation.parties]
          .sort((a, b) => Number(b === federation.candidate_party_id) - Number(a === federation.candidate_party_id))
          .map((id) => parties.find((candidate) => candidate.id === id))
          .filter((candidate): candidate is ElectionParty => candidate !== undefined)
      : [party];
    for (const member of members) placed.add(member.id);
    rows.push({
      key: federation ? `federation-${federation.id}` : `party-${party.id}`,
      parties: members,
      federation: federation ?? null,
    });
  }
  return rows;
}
