import { displayDayMonth, displayMonthShort } from "@/shared/lib/utils/display";
import type {
  CampaignActionKind,
  CampaignBand,
  CampaignEntry,
  CampaignEntryKind,
  CampaignRoll,
  CampaignTarget,
  DiceBand,
  GovernmentNotice,
  VoterGroup,
} from "@/types";
import { GROUP_INFO, nextPollDate } from "./voters";

/** O nome, a frase de cada ação e como ela aparece em "no comício" e "Eventos em ago". */
export const ACTION_INFO: Record<
  CampaignActionKind,
  { label: string; blurb: string; dice: string; noun: string; plural: string; at: string }
> = {
  TV: {
    label: "TV",
    blurb: "Todos os grupos, pelo peso",
    dice: "dois dados, vale o maior",
    noun: "TV",
    plural: "TV",
    at: "na TV",
  },
  EVENT: {
    label: "Evento com um grupo",
    blurb: "Um grupo; também repara a rejeição",
    dice: "dado",
    noun: "Evento",
    plural: "Eventos",
    at: "no evento",
  },
  RALLY: {
    label: "Comício",
    blurb: "Um grupo, barato e arriscado",
    dice: "dado com extremos dobrados",
    noun: "Comício",
    plural: "Comícios",
    at: "no comício",
  },
  ATTACK: {
    label: "Ataque ao rival",
    blurb: "Um grupo e um partido rival",
    dice: "dado",
    noun: "Ataque",
    plural: "Ataques",
    at: "no ataque",
  },
};

type BandStyle = {
  label: string;
  text: string;
  soft: string;
  fill: string;
  stroke: string;
  badge: "destructive" | "warning" | "secondary" | "success" | "info";
};

/** Rótulo e classes de cor de cada faixa do dado; as cores são tokens do tema. */
export const BAND_INFO: Record<DiceBand, BandStyle> = {
  DISASTER: {
    label: "Desastre",
    text: "text-destructive",
    soft: "bg-destructive-soft",
    fill: "fill-destructive-soft",
    stroke: "stroke-destructive",
    badge: "destructive",
  },
  WEAK: {
    label: "Fraco",
    text: "text-warning",
    soft: "bg-warning-soft",
    fill: "fill-warning-soft",
    stroke: "stroke-warning",
    badge: "warning",
  },
  NORMAL: {
    label: "Normal",
    text: "text-muted-foreground",
    soft: "bg-muted",
    fill: "fill-muted",
    stroke: "stroke-muted-foreground",
    badge: "secondary",
  },
  GOOD: {
    label: "Bom",
    text: "text-success",
    soft: "bg-success-soft",
    fill: "fill-success-soft",
    stroke: "stroke-success",
    badge: "success",
  },
  VIRAL: {
    label: "Viralizou",
    text: "text-primary",
    soft: "bg-info-soft",
    fill: "fill-info-soft",
    stroke: "stroke-primary",
    badge: "info",
  },
};

/** "+3", "−6,5" ou "0": o sinal na frente, vírgula decimal e no máximo `digits` casas. */
export function signed(value: number | string, digits = 2) {
  const number = Number(value);
  const text = Math.abs(number).toLocaleString("pt-BR", { maximumFractionDigits: digits });
  if (text === "0") return "0";
  return `${number > 0 ? "+" : "−"}${text}`;
}

/** O retorno decrescente em porcentagem, arredondado para baixo e nunca zero: 100%, 50%, 25%, 12%... */
export function ratePercent(rate: number | string) {
  return `${Math.max(1, Math.floor(Number(rate) * 100))}%`;
}

/** "1", "2–6" ou "15–19": onde a faixa cai no d20. */
export function bandRange(band: CampaignBand) {
  return band.first_roll === band.last_roll ? `${band.first_roll}` : `${band.first_roll}–${band.last_roll}`;
}

/** A chance da faixa em porcentagem, com casas só quando há (0,25%). */
export function chancePercent(chance: number | string) {
  return `${(Number(chance) * 100).toLocaleString("pt-BR", { maximumFractionDigits: 2 })}%`;
}

/** O que a faixa muda: o apoio, ou a rejeição de quem agiu quando o apoio não muda (a culatra do ataque). */
export function bandEffect(band: CampaignBand) {
  if (Number(band.support) !== 0) return signed(band.support);
  if (Number(band.rejection) !== 0) return `${signed(band.rejection)} rej.`;
  return "0";
}

/** A faixa onde o número rolado cai. */
export function bandOf(bands: CampaignBand[], roll: number) {
  return bands.find((band) => roll >= band.first_roll && roll <= band.last_roll);
}

/** O grupo em minúsculas dentro de uma frase: "aposentados", "carteira". */
export function groupWord(group: VoterGroup) {
  return GROUP_INFO[group].short.toLowerCase();
}

/** Dia 1º do mês seguinte, quando o retorno decrescente volta a 100%. */
export function nextMonthLabel(today: string) {
  return displayDayMonth(nextPollDate(today));
}

export function monthLabel(today: string) {
  return displayMonthShort(today);
}

/** O alvo da ação escolhida: o grupo, ou o único alvo da TV. */
export function targetOf(targets: CampaignTarget[], group: VoterGroup | null) {
  return targets.find((target) => target.group === group);
}

/** Quanto do limite de reparação da campanha já foi usado no grupo. */
export function repairUsed(target: CampaignTarget) {
  return Number(target.repair_limit) - Number(target.repair_left);
}

const ENTRY_LABEL: Record<CampaignEntryKind, string> = {
  TV: "TV",
  EVENT: "Evento",
  RALLY: "Comício",
  ATTACK: "Ataque",
  BASE_BUDGET: "Verba de base",
  ATTACK_RECEIVED: "Ataque recebido",
};

/** "Evento com aposentados", "Ataque ao FDS entre servidores": o título de uma linha do histórico. */
export function entryTitle(entry: CampaignEntry) {
  const label = ENTRY_LABEL[entry.kind];
  const group = entry.group ? groupWord(entry.group) : null;
  switch (entry.kind) {
    case "EVENT":
    case "RALLY":
      return group ? `${label} com ${group}` : label;
    case "ATTACK":
      return `Ataque ao ${entry.rival_abbr ?? "rival"}${group ? ` entre ${group}` : ""}`;
    case "ATTACK_RECEIVED":
      return `${entry.party_abbr} atacou${group ? ` entre ${group}` : ""}`;
    default:
      return label;
  }
}

/** O efeito no dia em uma linha: "+3 · −1 rej.", "FDS −5", "+3 em cada". */
export function effectText(entry: CampaignEntry) {
  const support = Number(entry.support);
  const rejection = Number(entry.rejection);
  const parts: string[] = [];
  if (support !== 0) {
    const value = signed(support);
    if (entry.kind === "ATTACK") parts.push(`${entry.rival_abbr ?? ""} ${value}`.trim());
    else if (entry.group === null && entry.kind !== "ATTACK_RECEIVED") parts.push(`${value} em cada`);
    else parts.push(value);
  }
  if (rejection !== 0) parts.push(`${signed(rejection)} rej.`);
  return parts.length > 0 ? parts.join(" · ") : "0";
}

/** A frase do resultado do dado, no topo do diálogo. */
export function resultTitle(roll: CampaignRoll) {
  const { entry } = roll;
  const group = entry.group ? groupWord(entry.group) : null;
  const where = group ? `entre ${group}` : "em cada grupo";
  const support = Number(entry.support);

  if (entry.kind === "ATTACK") {
    if (entry.band === "DISASTER") return `O tiro saiu pela culatra: ${signed(entry.rejection)} de rejeição ${where}`;
    return `Ataque ao ${entry.rival_abbr}: ${signed(support)} de apoio do ${entry.rival_abbr} ${where}`;
  }
  const info = ACTION_INFO[entry.kind as CampaignActionKind];
  if (entry.band === "DISASTER") return `Desastre ${info.at}: ${signed(support)} de apoio ${where}`;
  if (entry.band === "VIRAL") return `Viralizou: ${signed(support)} de apoio ${where}`;
  if (entry.kind === "TV") return `TV: ${signed(support)} de apoio ${where}`;
  return `${info.noun} com ${group}: ${signed(support)} de apoio`;
}

/** A manchete que o desastre, o viral e todo ataque merecem; sem jornal na partida, ela fecha o diálogo do dado. */
export function headline(entry: CampaignEntry) {
  const group = entry.group ? groupWord(entry.group) : null;
  if (entry.kind === "ATTACK") {
    return `${entry.party_abbr} parte para o ataque contra o ${entry.rival_abbr}${group ? ` entre ${group}` : ""}`;
  }
  const info = ACTION_INFO[entry.kind as CampaignActionKind];
  const withGroup = group ? ` com ${group}` : "";
  if (entry.band === "DISASTER")
    return `Candidato do ${entry.party_abbr} se envolve em polêmica ${info.at}${withGroup}`;
  return `${info.noun} do ${entry.party_abbr}${withGroup} viraliza`;
}

export type CampaignToast = { tone: "info" | "warning"; title: string; description: string };

const capitalize = (text: string) => `${text.charAt(0).toUpperCase()}${text.slice(1)}`;

/**
 * O aviso de uma ação de campanha para quem vê: o ataque contra o partido dele e a ação de outro
 * filiado do mesmo partido. O que é público (todo ataque, o viral e o desastre) sai no jornal da partida.
 */
export function campaignToast(
  notice: GovernmentNotice,
  mine: { abbr: string; nickname: string } | undefined,
): CampaignToast | null {
  const kind = notice.campaign_action;
  if (!kind) return null;
  const abbr = notice.party_abbr ?? "";
  const where = capitalize(notice.group ? `entre ${groupWord(notice.group)}` : "em todos os grupos");

  if (kind === "ATTACK") {
    if (mine && notice.rival_abbr === mine.abbr) {
      return {
        tone: "warning",
        title: `O ${abbr} atacou o ${mine.abbr}`,
        description: `${where}. O efeito aparece no histórico da campanha.`,
      };
    }
    return null;
  }
  if (mine && mine.abbr === abbr && notice.actor !== mine.nickname) {
    return {
      tone: "info",
      title: `${notice.actor} fez ${ACTION_INFO[kind].noun.toLowerCase()} no ${abbr}`,
      description: `${where}. O resultado do dado está no histórico.`,
    };
  }
  return null;
}
