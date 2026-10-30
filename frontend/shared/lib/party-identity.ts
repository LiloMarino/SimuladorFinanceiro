import { z } from "zod";
import type { VoterValue } from "@/types";
import { FLAGS_PER_PARTY } from "./party-flags";

const ABBR_PATTERN = /^[A-ZÀ-Ý]{2,8}$/;

/** A identidade de um partido: a mesma ao fundar no governo e ao preparar o Meu partido no lobby. */
export const partyIdentitySchema = z.object({
  name: z.string().trim().min(2, "Dê um nome de pelo menos 2 letras.").max(60, "O nome vai até 60 letras."),
  abbr: z.string().regex(ABBR_PATTERN, "A sigla tem de 2 a 8 letras."),
  color: z.string().regex(/^#[0-9A-Fa-f]{6}$/, "Escolha uma cor."),
  flags: z
    .array(z.custom<VoterValue>())
    .length(FLAGS_PER_PARTY, `Escolha mais uma bandeira: o partido precisa de ${FLAGS_PER_PARTY}.`),
});
