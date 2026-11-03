import { useState } from "react";
import { Controller, useForm, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Clock, TriangleAlert } from "lucide-react";
import { ContributionField } from "@/shared/components/contribution-field";
import { FlagCards } from "@/shared/components/flag-cards";
import { PartyIdentityFields } from "@/shared/components/party-identity-fields";
import { PartyMark } from "@/shared/components/party-mark";
import { PlayerOption } from "@/shared/components/player-option";
import { ValueChip } from "@/shared/components/value-chip";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Field, FieldLabel } from "@/shared/components/ui/field";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/shared/components/ui/select";
import { contributionAmount, contributionText } from "@/shared/lib/contribution";
import { PARTY_COLORS } from "@/shared/lib/party-colors";
import { partyIdentitySchema } from "@/shared/lib/party-identity";
import { displayMoneyWhole } from "@/shared/lib/utils/display";
import type { PartyIdentity, VoterValue } from "@/types";
import { useSaveMyParty } from "../../hooks/mutations/useSaveMyParty";
import { useSavePartyContribution } from "../../hooks/mutations/useSavePartyContribution";
import { useSetPreparation } from "../../hooks/mutations/useSetPreparation";
import { cashShare, closeRivalTag, rivalsOf, sharedFlags, type Rival } from "../../lib/preparation";
import { PreparationFooter } from "./preparation-footer";
import { PreparationSection } from "./preparation-section";
import type { PartyModeProps } from "./party-tab";

const NO_VICE = "none";
const EMPTY_PARTY: PartyIdentity = { name: "", abbr: "", color: PARTY_COLORS[0], flags: [] };

/** Fundar o meu partido: identidade e bandeiras à esquerda; chapa, contribuição e com quem divide eleitor à direita. */
export function PartyFoundTab({
  preparations,
  mine,
  me,
  saved,
  contribution,
  humans,
  nickname,
  rules,
  savedSimulation,
  lead,
  locked,
  onClose,
}: PartyModeProps) {
  const form = useForm<PartyIdentity>({
    resolver: zodResolver(partyIdentitySchema),
    values: saved ?? EMPTY_PARTY,
  });
  const flags = useWatch({ control: form.control, name: "flags" });
  const founding = me?.kind === "FOUND" ? me : undefined;
  const [candidate, setCandidate] = useState(founding?.candidate ?? nickname);
  const [vice, setVice] = useState(founding?.vice ?? mine.invited ?? NO_VICE);
  const [amount, setAmount] = useState(contributionText(contribution));
  const [error, setError] = useState<string | null>(null);
  const saveParty = useSaveMyParty();
  const saveContribution = useSavePartyContribution();
  const prepare = useSetPreparation();
  const saving = saveParty.isPending || saveContribution.isPending || prepare.isPending;

  const members = preparations.players
    .filter((p) => p.kind === "JOIN" && p.founder === nickname)
    .map((p) => p.nickname);
  const candidates = [nickname, ...members];
  const viceOptions = humans.filter((player) => player.nickname !== candidate);
  // O vice sai da chapa quando vira o candidato
  const viceValue = vice === candidate ? NO_VICE : vice;
  const rivals = rivalsOf(preparations, nickname);
  const takenColors = rivals.flatMap((rival) => (rival.color ? [rival.color] : []));

  // Grava a identidade e a contribuição no perfil e só depois a escolha da sala, que parte do perfil
  const submit = form.handleSubmit(async (party) => {
    setError(null);
    try {
      await saveParty.mutateAsync(party);
      await saveContribution.mutateAsync(contributionAmount(amount));
      await prepare.mutateAsync({ kind: "FOUND", candidate, vice: viceValue === NO_VICE ? null : viceValue });
    } catch (err) {
      setError((err as Error).message);
    }
  });

  return (
    <form onSubmit={(event) => void submit(event)} className="grid min-h-0 grid-rows-[minmax(0,1fr)_auto]">
      <div className="grid min-h-0 content-start gap-4.5 overflow-y-auto px-6 py-5">
        {lead}
        <fieldset
          disabled={locked}
          className="grid min-w-0 grid-cols-[minmax(0,1.15fr)_minmax(0,1fr)] items-start gap-6 disabled:opacity-55"
        >
          {/* Identidade e bandeiras */}
          <div className="grid min-w-0 gap-4.5">
            <PreparationSection title="Identidade" hint="salva no perfil">
              <PartyIdentityFields control={form.control} takenColors={takenColors} idPrefix="prep-party" />
            </PreparationSection>
            <Controller
              control={form.control}
              name="flags"
              render={({ field, fieldState }) => (
                <FlagCards
                  value={field.value}
                  onChange={field.onChange}
                  tag={closeRivalTag(field.value, rivals)}
                  columns={2}
                  error={fieldState.error?.message}
                />
              )}
            />
          </div>

          {/* Chapa, contribuição e rivais */}
          <div className="grid min-w-0 gap-4.5">
            <PreparationSection title="Chapa" hint="só nesta sala">
              <div className="grid grid-cols-2 gap-3">
                <Field>
                  <FieldLabel>Candidato</FieldLabel>
                  <Select
                    value={candidate}
                    items={Object.fromEntries(
                      candidates.map((name) => [name, name === nickname ? `${name} (você)` : name]),
                    )}
                    onValueChange={(value) => value && setCandidate(value)}
                  >
                    <SelectTrigger className="w-full" aria-label="Candidato">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {candidates.map((name) => (
                        <SelectItem key={name} value={name}>
                          {name === nickname ? `${name} (você)` : name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </Field>
                <Field>
                  <FieldLabel>Vice</FieldLabel>
                  <Select
                    value={viceValue}
                    items={{
                      [NO_VICE]: "Sem vice",
                      ...Object.fromEntries(
                        viceOptions.map((player) => [
                          player.nickname,
                          <PlayerOption key={player.nickname} nickname={player.nickname} color={player.color} />,
                        ]),
                      ),
                    }}
                    onValueChange={(value) => value && setVice(value)}
                  >
                    <SelectTrigger className="w-full" aria-label="Vice">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value={NO_VICE}>Sem vice</SelectItem>
                      {viceOptions.map((player) => (
                        <SelectItem key={player.nickname} value={player.nickname}>
                          <PlayerOption nickname={player.nickname} color={player.color} />
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </Field>
              </div>
              {mine.invited && mine.invited === viceValue && (
                <Badge variant="warning" className="justify-self-start">
                  <Clock /> Convite enviado · {mine.invited} ainda não respondeu
                </Badge>
              )}
            </PreparationSection>

            <PreparationSection title="Contribuição mensal" hint="vale fundando ou entrando">
              <ContributionField
                id="prep-found-contribution"
                value={amount}
                onChange={setAmount}
                note={`${cashShare(contributionAmount(amount), rules.starting_cash)} do saldo inicial desta sala (${displayMoneyWhole(rules.starting_cash)}). Cobrada no 1º dia útil de cada mês da campanha. Mês sem caixa vira pendência.`}
              />
            </PreparationSection>

            <SharedVoters flags={flags} rivals={rivals} />
          </div>
        </fieldset>

        {/* Conflitos que travam o Iniciar */}
        {preparations.conflicts.length > 0 && (
          <Alert variant="destructive">
            <TriangleAlert />
            <AlertTitle>Há partidos em conflito: o host não consegue iniciar</AlertTitle>
            <AlertDescription>
              <ul className="list-disc pl-4">
                {preparations.conflicts.map((conflict) => (
                  <li key={conflict}>{conflict}</li>
                ))}
              </ul>
            </AlertDescription>
          </Alert>
        )}
      </div>

      <PreparationFooter
        note={
          savedSimulation
            ? "Travado com partida salva selecionada."
            : "Fica no seu perfil: identidade, bandeiras e contribuição. Só nesta sala: a chapa."
        }
        error={error}
        saving={saving}
        canSave={!locked}
        onClose={onClose}
      />
    </form>
  );
}

/** "Com quem você divide eleitor": cada partido da sala com as bandeiras que repete as suas. */
function SharedVoters({ flags, rivals }: { flags: VoterValue[]; rivals: Rival[] }) {
  const rows = rivals
    .map((rival) => ({ rival, shared: sharedFlags(flags, rival) }))
    .sort((a, b) => b.shared.length - a.shared.length);
  const closest = rows[0];
  return (
    <div className="grid gap-1.5 rounded-[10px] border px-3.5 py-3">
      <div className="grid gap-0.5">
        <b className="text-[13.5px] font-semibold">Com quem você divide eleitor</b>
        <span className="text-xs text-muted-foreground">
          Bandeira em comum disputa o mesmo grupo de eleitores.
          {closest &&
            closest.shared.length >= 2 &&
            ` Com ${closest.shared.length} de 3 iguais, você e o ${closest.rival.abbr} largam brigando pelo mesmo voto.`}
        </span>
      </div>
      {rows.map(({ rival, shared }) => (
        <div
          key={rival.abbr}
          className="grid grid-cols-[2.75rem_minmax(0,1fr)_auto] items-center gap-2.5 border-t border-muted py-2"
        >
          <PartyMark abbr={rival.abbr} color={rival.color} size="sm" />
          <div className="grid min-w-0 gap-1">
            <span className="truncate text-[12.5px]" title={rival.name}>
              {rival.name} · {rival.founder ?? "computador"}
            </span>
            {shared.length > 0 && (
              <span className="flex flex-wrap gap-1">
                {shared.map((flag) => (
                  <ValueChip key={flag} value={flag} />
                ))}
              </span>
            )}
          </div>
          <Badge variant={shared.length === 0 ? "success" : shared.length === 1 ? "secondary" : "warning"} size="sm">
            {shared.length === 0 ? "nenhuma" : shared.length === 1 ? "1 bandeira" : `${shared.length} bandeiras`}
          </Badge>
        </div>
      ))}
    </div>
  );
}
