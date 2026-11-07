import type { CampaignActionKind, VoterGroup } from "@/types";
import { groupWord } from "../../lib/campaign";

export function summaryTitle(kind: CampaignActionKind, group: VoterGroup, rival: string | null) {
  switch (kind) {
    case "TV":
      return "TV";
    case "EVENT":
      return `Evento com ${groupWord(group)}`;
    case "RALLY":
      return `Comício com ${groupWord(group)}`;
    case "ATTACK":
      return `Ataque ao ${rival ?? "rival"} entre ${groupWord(group)}`;
  }
}
