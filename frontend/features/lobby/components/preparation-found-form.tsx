import { useState } from "react";
import { Controller, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { FlagCards } from "@/shared/components/flag-cards";
import { PartyIdentityFields } from "@/shared/components/party-identity-fields";
import { Button } from "@/shared/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/shared/components/ui/select";
import { Field, FieldLabel } from "@/shared/components/ui/field";
import { Spinner } from "@/shared/components/ui/spinner";
import { PARTY_COLORS } from "@/shared/lib/party-colors";
import { partyIdentitySchema } from "@/shared/lib/party-identity";
import type { PartyIdentity, PlayerPreparation, RoomPlayer } from "@/types";
import { useSaveMyParty } from "../hooks/mutations/useSaveMyParty";
import { useSetPreparation } from "../hooks/mutations/useSetPreparation";

const NO_VICE = "none";
const EMPTY_PARTY: PartyIdentity = { name: "", abbr: "", color: PARTY_COLORS[0], flags: [] };

type PreparationFoundFormProps = {
  /** O Meu partido salvo; nulo quando o jogador ainda não salvou um */
  saved: PartyIdentity | null;
  nickname: string;
  /** Humanos na sala, para o vice */
  humans: RoomPlayer[];
  /** O que o jogador já preparou, quando fundou */
  mine: PlayerPreparation | undefined;
  /** Quem preparou entrar no partido deste jogador: candidatos possíveis além dele */
  members: string[];
  /** Cores dos partidos que os outros jogadores já preparam */
  takenColors: string[];
  onError: (message: string | null) => void;
};

/** Fundar o Meu partido na abertura da campanha: identidade, bandeiras, candidato e vice. */
export function PreparationFoundForm({
  saved,
  nickname,
  humans,
  mine,
  members,
  takenColors,
  onError,
}: PreparationFoundFormProps) {
  const form = useForm<PartyIdentity>({
    resolver: zodResolver(partyIdentitySchema),
    values: saved ?? EMPTY_PARTY,
  });
  const [candidate, setCandidate] = useState(mine?.candidate ?? nickname);
  const [vice, setVice] = useState(mine?.vice ?? NO_VICE);
  const save = useSaveMyParty();
  const prepare = useSetPreparation();
  const busy = save.isPending || prepare.isPending;

  const candidates = [nickname, ...members];
  const viceOptions = humans.map((p) => p.nickname).filter((name) => name !== candidate);
  // O vice sai da chapa quando vira o candidato
  const viceValue = vice === candidate ? NO_VICE : vice;

  const submit = form.handleSubmit((party) =>
    save.mutate(party, {
      onSuccess: () =>
        prepare.mutate(
          { kind: "FOUND", candidate, vice: viceValue === NO_VICE ? null : viceValue },
          { onSuccess: () => onError(null), onError: (err) => onError(err.message) },
        ),
      onError: (err) => onError(err.message),
    }),
  );

  return (
    <form onSubmit={(event) => void submit(event)} className="grid gap-3.5">
      <PartyIdentityFields control={form.control} takenColors={takenColors} idPrefix="prep-party" />

      <Controller
        control={form.control}
        name="flags"
        render={({ field, fieldState }) => (
          <FlagCards value={field.value} onChange={field.onChange} error={fieldState.error?.message} />
        )}
      />

      {/* Chapa */}
      <div className="grid gap-3 sm:grid-cols-2">
        <Field>
          <FieldLabel>Candidato</FieldLabel>
          <Select
            value={candidate}
            items={Object.fromEntries(candidates.map((name) => [name, name]))}
            onValueChange={(value) => value && setCandidate(value)}
          >
            <SelectTrigger className="w-full" aria-label="Candidato">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {candidates.map((name) => (
                <SelectItem key={name} value={name}>
                  {name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </Field>
        <Field>
          <FieldLabel>Vice</FieldLabel>
          <Select
            value={viceValue}
            items={{ [NO_VICE]: "Sem vice", ...Object.fromEntries(viceOptions.map((name) => [name, name])) }}
            onValueChange={(value) => value && setVice(value)}
          >
            <SelectTrigger className="w-full" aria-label="Vice">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value={NO_VICE}>Sem vice</SelectItem>
              {viceOptions.map((name) => (
                <SelectItem key={name} value={name}>
                  {name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </Field>
      </div>

      <Button type="submit" disabled={busy} className="justify-self-start">
        {busy && <Spinner />}
        {mine ? "Atualizar a preparação" : "Preparar este partido"}
      </Button>
    </form>
  );
}
